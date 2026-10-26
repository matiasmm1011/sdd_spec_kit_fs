<#
.SYNOPSIS
    Coordina el reparto de tareas del equipo a partir de asignaciones.md.

.DESCRIPTION
    Acciones:
      listar      Muestra las tareas de cada integrante y su estado (hecha, lista o bloqueada).
      siguiente   Indica la próxima tarea que puedes hacer tú (o si estás bloqueado o terminaste).
      esperar     Hace git fetch cada cierto tiempo hasta que una tarea tuya se desbloquee.
      subir       Marca la tarea con [X] en tasks.md, hace commit, git pull --rebase y git push.

    Una tarea está "hecha" cuando aparece como [X] en tasks.md (en origin/main o en tu copia local).
    Una tarea está "bloqueada" cuando alguna de sus dependencias aún no está hecha. Las dependencias
    salen de los textos "(después de Txxx)" de asignaciones.md y de "dependencias" en equipo.json.

    Códigos de salida:
      0   Éxito (o tarea lista / desbloqueada)
      10  Todas tus tareas están hechas
      11  Tus tareas pendientes están bloqueadas
      12  Se agotó el tiempo de espera
      20  Conflicto al hacer git pull --rebase (hay que resolverlo a mano)
      21  Hay cambios fuera de tu capa (usa -PermitirOtrasCapas si lo coordinaste)
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidateSet('listar', 'siguiente', 'esperar', 'subir')]
    [string]$Accion,

    # Nombre (o parte del nombre) del integrante. Si se omite se deduce de git config.
    [string]$Persona,

    # Para 'subir': ID de la tarea terminada, por ejemplo T030.
    [string]$Tarea,

    # Para 'esperar': segundos entre cada git fetch y tiempo máximo de espera.
    [int]$Intervalo = 0,
    [int]$MaxSegundos = 0,

    # Para 'subir': línea de coautoría que se añade al commit (opcional).
    [string]$Coautor = '',

    [switch]$PermitirOtrasCapas,

    # Para 'subir': solo muestra lo que haría, sin modificar nada.
    [switch]$Simular
)

$ErrorActionPreference = 'Stop'
try {
    [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
    $OutputEncoding = [Console]::OutputEncoding
} catch { }

# --- Utilidades ------------------------------------------------------------

function Invoke-Git {
    # Sin bloque param: así opciones como -A o -m llegan a git y no se confunden
    # con abreviaturas de parámetros de PowerShell.
    $previo = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try { $salida = & git @args 2>&1 | ForEach-Object { "$_" } }
    finally { $ErrorActionPreference = $previo }
    $script:CodigoGit = $LASTEXITCODE
    return $salida
}

function Normalizar([string]$texto) {
    $descompuesto = $texto.Normalize([System.Text.NormalizationForm]::FormD)
    $letras = $descompuesto.ToCharArray() | Where-Object {
        [System.Globalization.CharUnicodeInfo]::GetUnicodeCategory($_) -ne 'NonSpacingMark'
    }
    return (-join $letras).ToLowerInvariant()
}

function Recortar([string]$texto, [int]$largo) {
    if ($texto.Length -le $largo) { return $texto }
    return $texto.Substring(0, $largo - 3) + '...'
}

$raiz = (Invoke-Git rev-parse --show-toplevel | Select-Object -First 1)
if ($script:CodigoGit -ne 0) { throw 'Este script debe ejecutarse dentro del repositorio git del proyecto.' }
Set-Location $raiz

$dirSkill = Split-Path -Parent $PSScriptRoot
$config = Get-Content (Join-Path $dirSkill 'equipo.json') -Raw -Encoding UTF8 | ConvertFrom-Json

# --- Lectura de asignaciones.md -------------------------------------------

function Leer-Asignaciones {
    $ruta = Join-Path $raiz $config.asignaciones
    if (-not (Test-Path $ruta)) {
        throw "No se encontró $($config.asignaciones). Ejecuta git pull --rebase origin $($config.rama)."
    }
    $lineas = Get-Content $ruta -Encoding UTF8

    $personas = @()
    $actual = $null
    $rutaTasks = $null
    foreach ($linea in $lineas) {
        if ($linea -match '\*\*Fuente\*\*:\s*\[[^\]]*\]\(([^)]+)\)') { $rutaTasks = $Matches[1]; continue }
        if ($linea -match '^##\s+(?<n>.+?)\s+[—–-]\s+(?<r>.+?)\s+\(\d+ tareas\)') {
            $actual = [pscustomobject]@{ Nombre = $Matches['n'].Trim(); Rol = $Matches['r'].Trim(); Tareas = @() }
            $personas += $actual
            continue
        }
        if ($actual -and $linea -match '^\|\s*(?<id>T\d{3})\s*\|\s*(?<h>[^|]*?)\s*\|\s*(?<t>.*?)\s*\|\s*$') {
            $actual.Tareas += [pscustomobject]@{
                Id = $Matches['id']; Historia = $Matches['h']; Texto = $Matches['t']
            }
        }
    }
    if (-not $rutaTasks) { throw 'asignaciones.md no indica el archivo tasks.md (línea "**Fuente**: [...](ruta)").' }
    if ($personas.Count -eq 0) { throw 'No se encontraron integrantes en asignaciones.md.' }

    $dueno = @{}
    $deps = @{}
    foreach ($p in $personas) {
        foreach ($t in $p.Tareas) {
            $dueno[$t.Id] = $p
            $deps[$t.Id] = New-Object System.Collections.Generic.List[string]
            foreach ($m in [regex]::Matches($t.Texto, 'despu.s de (T\d{3})')) { $deps[$t.Id].Add($m.Groups[1].Value) }
        }
    }
    foreach ($propiedad in $config.dependencias.PSObject.Properties) {
        if (-not $deps.ContainsKey($propiedad.Name)) { continue }
        foreach ($d in $propiedad.Value) {
            if (-not $deps[$propiedad.Name].Contains($d)) { $deps[$propiedad.Name].Add($d) }
        }
    }
    return [pscustomobject]@{ Personas = $personas; RutaTasks = $rutaTasks; Dueno = $dueno; Deps = $deps }
}

function Leer-Hechas([string]$rutaTasks) {
    $hechas = New-Object 'System.Collections.Generic.HashSet[string]'
    $contenidos = @()
    $local = Join-Path $raiz $rutaTasks
    if (Test-Path $local) { $contenidos += Get-Content $local -Encoding UTF8 }
    $remoto = Invoke-Git show "origin/$($config.rama):$rutaTasks"
    if ($script:CodigoGit -eq 0) { $contenidos += $remoto }
    foreach ($linea in $contenidos) {
        if ($linea -match '^- \[[xX]\] (T\d{3})\b') { [void]$hechas.Add($Matches[1]) }
    }
    return , $hechas
}

function Obtener-Estado($datos, $hechas, [string]$id) {
    if ($hechas.Contains($id)) { return [pscustomobject]@{ Id = $id; Estado = 'hecha'; Faltan = @() } }
    $faltan = @($datos.Deps[$id] | Where-Object { -not $hechas.Contains($_) })
    if ($faltan.Count -gt 0) { return [pscustomobject]@{ Id = $id; Estado = 'bloqueada'; Faltan = $faltan } }
    return [pscustomobject]@{ Id = $id; Estado = 'lista'; Faltan = @() }
}

function Resolver-Persona($datos) {
    if ($Persona) {
        # -Persona puede ser un alias de git (usuario o correo) o parte del nombre.
        foreach ($p in $datos.Personas) {
            foreach ($a in @($config.alias.$($p.Nombre))) {
                if ($a -and $a -ieq $Persona) { return $p }
            }
        }
        $buscada = Normalizar $Persona
        $coinciden = @($datos.Personas | Where-Object { (Normalizar $_.Nombre).Contains($buscada) })
        if ($coinciden.Count -eq 1) { return $coinciden[0] }
        throw "No pude identificar a '$Persona'. Integrantes: $(($datos.Personas | ForEach-Object { $_.Nombre }) -join ', ')."
    }

    $usuario = (Invoke-Git config user.name | Select-Object -First 1)
    $correo = (Invoke-Git config user.email | Select-Object -First 1)

    # 1) Alias exactos definidos en equipo.json (usuario de git o correo).
    foreach ($p in $datos.Personas) {
        $alias = $config.alias.$($p.Nombre)
        foreach ($a in @($alias)) {
            if ($a -and ($a -ieq $usuario -or $a -ieq $correo)) { return $p }
        }
    }

    # 2) Coincidencia aproximada: el nombre de pila o el apellido aparece en el usuario o el correo.
    $huella = Normalizar "$usuario $correo"
    $coinciden = @($datos.Personas | Where-Object {
        $tokens = (Normalizar $_.Nombre) -split '\s+' | Where-Object { $_.Length -ge 4 }
        @($tokens | Where-Object { $huella.Contains($_) }).Count -gt 0
    })
    if ($coinciden.Count -eq 1) { return $coinciden[0] }

    throw ("No pude saber quién eres (git user.name='$usuario', user.email='$correo'). " +
        "Vuelve a ejecutar con -Persona '<nombre>' o añade tu usuario de git en equipo.json > alias.")
}

function Calcular($datos, $yo) {
    $hechas = Leer-Hechas $datos.RutaTasks
    $mias = @($yo.Tareas | ForEach-Object { Obtener-Estado $datos $hechas $_.Id })
    return [pscustomobject]@{ Hechas = $hechas; Mias = $mias }
}

function Texto-De($datos, [string]$id) {
    return ($datos.Dueno[$id].Tareas | Where-Object { $_.Id -eq $id } | Select-Object -First 1).Texto
}

function Nombre-Faltantes($datos, $faltan) {
    $faltan = @($faltan)
    $mostradas = if ($faltan.Count -gt 4) { $faltan[0..2] } else { $faltan }
    $texto = ($mostradas | ForEach-Object {
        $responsable = if ($datos.Dueno.ContainsKey($_)) { $datos.Dueno[$_].Nombre } else { 'otra fase' }
        "$_ ($responsable)"
    }) -join ', '
    if ($faltan.Count -gt 4) { $texto += " y $($faltan.Count - 3) más" }
    return $texto
}

# --- Acciones -------------------------------------------------------------

function Accion-Listar($datos, $yo) {
    $hechas = Leer-Hechas $datos.RutaTasks
    Write-Output "Tareas del equipo (según origin/$($config.rama) y tu copia local)"
    Write-Output "Tú eres: $($yo.Nombre) - $($yo.Rol)"
    Write-Output "Leyenda: [x] hecha, [>] lista para hacer, [ ] bloqueada"
    foreach ($p in $datos.Personas) {
        $estados = @($p.Tareas | ForEach-Object { Obtener-Estado $datos $hechas $_.Id })
        $hechasP = @($estados | Where-Object { $_.Estado -eq 'hecha' }).Count
        $marca = if ($p.Nombre -eq $yo.Nombre) { ' (tú)' } else { '' }
        Write-Output ''
        Write-Output "== $($p.Nombre) - $($p.Rol)${marca}: $hechasP/$($p.Tareas.Count) hechas =="
        foreach ($t in $p.Tareas) {
            $e = $estados | Where-Object { $_.Id -eq $t.Id }
            $simbolo = switch ($e.Estado) { 'hecha' { '[x]' } 'lista' { '[>]' } default { '[ ]' } }
            $nota = if ($e.Estado -eq 'bloqueada') { "  <- espera: $(Nombre-Faltantes $datos $e.Faltan)" } else { '' }
            Write-Output ("  {0} {1} {2,-6} {3}{4}" -f $simbolo, $t.Id, $t.Historia, (Recortar $t.Texto 80), $nota)
        }
    }
}

function Accion-Siguiente($datos, $yo) {
    $calculo = Calcular $datos $yo
    $lista = $calculo.Mias | Where-Object { $_.Estado -eq 'lista' } | Select-Object -First 1
    if ($lista) {
        Write-Output "LISTA $($lista.Id)"
        Write-Output (Texto-De $datos $lista.Id)
        exit 0
    }
    $pendientes = @($calculo.Mias | Where-Object { $_.Estado -eq 'bloqueada' })
    if ($pendientes.Count -eq 0) {
        Write-Output 'TERMINADO: todas tus tareas están hechas.'
        exit 10
    }
    Write-Output 'BLOQUEADA: ninguna de tus tareas pendientes se puede hacer todavía.'
    foreach ($p in $pendientes) { Write-Output "  $($p.Id) espera $(Nombre-Faltantes $datos $p.Faltan)" }
    exit 11
}

function Accion-Esperar($datos, $yo) {
    $pausa = if ($Intervalo -gt 0) { $Intervalo } else { [int]$config.intervalo_segundos }
    $limite = if ($MaxSegundos -gt 0) { (Get-Date).AddSeconds($MaxSegundos) } else { (Get-Date).AddMinutes([int]$config.max_minutos_espera) }
    $ultimoAviso = ''
    $vueltas = 0

    while ($true) {
        Invoke-Git fetch origin --quiet | Out-Null
        if ($script:CodigoGit -ne 0) { Write-Output 'Aviso: no se pudo hacer git fetch (¿sin conexión?). Se reintentará.' }

        $calculo = Calcular $datos $yo
        $lista = @($calculo.Mias | Where-Object { $_.Estado -eq 'lista' })
        $pendientes = @($calculo.Mias | Where-Object { $_.Estado -eq 'bloqueada' })

        if ($lista.Count -gt 0 -or $pendientes.Count -eq 0) {
            if ($lista.Count -eq 0) { Write-Output 'TERMINADO: todas tus tareas están hechas.'; exit 10 }
            $limpio = @(Invoke-Git status --porcelain).Count -eq 0
            if ($limpio) {
                $salida = Invoke-Git pull --rebase origin $config.rama
                if ($script:CodigoGit -ne 0) { Write-Output $salida; Write-Output 'CONFLICTO al actualizar. Resuélvelo a mano.'; exit 20 }
                Write-Output 'Cambios del equipo descargados (git pull --rebase).'
            } else {
                Write-Output "Tienes cambios sin subir; haz git pull --rebase origin $($config.rama) cuando puedas."
            }
            Write-Output "DESBLOQUEADA $($lista[0].Id)"
            Write-Output (Texto-De $datos $lista[0].Id)
            exit 0
        }

        # Solo se muestran las tareas de otros integrantes de las que depende alguna tarea tuya.
        $externas = @($pendientes | ForEach-Object { $_.Faltan } | Sort-Object -Unique |
            Where-Object { -not $datos.Dueno.ContainsKey($_) -or $datos.Dueno[$_].Nombre -ne $yo.Nombre })
        $aviso = "Esperando a: $(Nombre-Faltantes $datos $externas)"
        if ($aviso -ne $ultimoAviso -or ($vueltas % 10) -eq 0) {
            Write-Output "[$(Get-Date -Format 'HH:mm:ss')] $aviso"
            $ultimoAviso = $aviso
        }
        $vueltas++

        if ((Get-Date) -gt $limite) {
            Write-Output 'TIEMPO AGOTADO: sigue bloqueado. Vuelve a ejecutar la espera si quieres seguir.'
            exit 12
        }
        Start-Sleep -Seconds $pausa
    }
}

function Rutas-Cambiadas {
    $rutas = @()
    foreach ($linea in @(Invoke-Git status --porcelain)) {
        if ($linea.Length -lt 4) { continue }
        $ruta = $linea.Substring(3).Trim('"')
        if ($ruta -match ' -> ') { $ruta = ($ruta -split ' -> ')[-1] }
        $rutas += $ruta.Replace('\', '/')
    }
    return $rutas
}

function Accion-Subir($datos, $yo) {
    if (-not $Tarea) { throw 'Indica la tarea con -Tarea Txxx.' }
    $id = $Tarea.ToUpperInvariant()
    $mia = $yo.Tareas | Where-Object { $_.Id -eq $id } | Select-Object -First 1
    if (-not $mia) { throw "La tarea $id no está asignada a $($yo.Nombre)." }

    $rama = (Invoke-Git rev-parse --abbrev-ref HEAD | Select-Object -First 1)
    if ($rama -ne $config.rama) { throw "Estás en la rama '$rama'; las tareas se suben desde '$($config.rama)'." }

    # Solo se toca la capa propia (más tasks.md).
    $permitidos = @($config.propiedad.$($yo.Nombre)) + @($datos.RutaTasks)
    $fuera = @(Rutas-Cambiadas | Where-Object {
        $ruta = $_
        -not (@($permitidos | Where-Object { $ruta -like $_ }).Count -gt 0)
    })
    if ($fuera.Count -gt 0 -and -not $PermitirOtrasCapas) {
        Write-Output 'Hay cambios fuera de tu capa. Coordínalos con su responsable o usa -PermitirOtrasCapas:'
        $fuera | ForEach-Object { Write-Output "  $_" }
        exit 21
    }

    $titulo = ("$id`: " + ($mia.Texto -replace '[`"]', '')).Trim()
    $titulo = Recortar $titulo 72

    if ($Simular) {
        Write-Output "SIMULACIÓN: marcaría $id como [X] en $($datos.RutaTasks), haría commit '$titulo',"
        Write-Output "git pull --rebase origin $($config.rama) y git push origin $($config.rama)."
        exit 0
    }

    # Marca la casilla en tasks.md (si ya estaba marcada no cambia nada).
    $rutaTasks = Join-Path $raiz $datos.RutaTasks
    $codificacion = New-Object System.Text.UTF8Encoding($false)
    $texto = [System.IO.File]::ReadAllText($rutaTasks, $codificacion)
    $nuevo = [regex]::Replace($texto, "(?m)^(- )\[ \]( $id\b)", '$1[X]$2')
    if ($nuevo -ne $texto) { [System.IO.File]::WriteAllText($rutaTasks, $nuevo, $codificacion) }

    Invoke-Git add -A | Out-Null
    Invoke-Git diff --cached --quiet | Out-Null
    if ($script:CodigoGit -ne 0) {
        if ($Coautor) { Invoke-Git commit -q -m $titulo -m $Coautor | Out-Null } else { Invoke-Git commit -q -m $titulo | Out-Null }
        if ($script:CodigoGit -ne 0) { throw "git commit falló para $id." }
        Write-Output "Commit creado: $titulo"
    } else {
        Write-Output "No había cambios nuevos que confirmar para $id."
    }

    for ($intento = 1; $intento -le 3; $intento++) {
        $salida = Invoke-Git pull --rebase origin $config.rama
        if ($script:CodigoGit -ne 0) {
            Write-Output $salida
            Write-Output ('CONFLICTO al hacer git pull --rebase. Resuelve los archivos en conflicto, ' +
                "ejecuta git add y git rebase --continue, y luego git push origin $($config.rama).")
            exit 20
        }
        $salida = Invoke-Git push origin $config.rama
        if ($script:CodigoGit -eq 0) {
            Write-Output "SUBIDA $id a origin/$($config.rama)."
            exit 0
        }
        Write-Output "El push fue rechazado (intento $intento de 3); se actualiza y se reintenta."
    }
    Write-Output $salida
    throw "No se pudo hacer push de $id tras 3 intentos."
}

# --- Programa principal ----------------------------------------------------

$datos = Leer-Asignaciones
$yo = Resolver-Persona $datos

switch ($Accion) {
    'listar'    { Accion-Listar $datos $yo }
    'siguiente' { Accion-Siguiente $datos $yo }
    'esperar'   { Accion-Esperar $datos $yo }
    'subir'     { Accion-Subir $datos $yo }
}
