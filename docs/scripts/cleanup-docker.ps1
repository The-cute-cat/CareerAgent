# ============================================================
# CareerAgent Docker Compose 全量清理脚本 (PowerShell)
# 用途: 清理本 Docker Compose 产生的所有容器、镜像、
#       数据卷、网络及构建缓存
# 使用:
#   .\cleanup-docker.ps1           # 预览模式
#   .\cleanup-docker.ps1 -Force    # 执行清理（逐项确认）
#   .\cleanup-docker.ps1 -Yes      # 跳过确认，直接执行
#   .\cleanup-docker.ps1 -Help     # 显示帮助
# 注意: 此操作不可逆，所有数据库数据将被永久删除！
# ============================================================
[CmdletBinding()]
param(
    [switch]$Force,
    [switch]$Yes,
    [switch]$Help
)

# ---- 颜色辅助函数 ----
function Write-Header($text) {
    Write-Host ""
    Write-Host "=== $text ===" -ForegroundColor Cyan
}
function Write-Step($text) {
    Write-Host "  [OK] $text" -ForegroundColor Green
}
function Write-Warn($text) {
    Write-Host "  [!!] $text" -ForegroundColor Yellow
}
function Write-Danger($text) {
    Write-Host "  [X] $text" -ForegroundColor Red
}

# ---- 项目常量 ----
$ComposeFile   = "docker-compose.yml"
$ProjectName   = "careeragent"
$NetworkName   = "career-network"

$NamedVolumes = @(
    "career-mysql-data",
    "career-redis-data",
    "career-neo4j-data",
    "career-neo4j-logs",
    "career-rabbitmq-data",
    "career-ai-data",
    "career-ai-logs",
    "career-milvus-data"
)

$BuiltImages = @(
    "careeragent-backend:latest",
    "careeragent-frontend:latest",
    "careeragent-ai-service:latest"
)

$DependencyImages = @(
    "docker.1ms.run/mysql:8.0",
    "docker.1ms.run/redis:7-alpine",
    "docker.1ms.run/neo4j:5-community",
    "docker.1ms.run/rabbitmq:3-management-alpine",
    "docker.1ms.run/milvusdb/milvus:v2.4.14"
)

# ---- 帮助信息 ----
if ($Help) {
    Write-Host "用法: .\cleanup-docker.ps1 [-Force] [-Yes] [-Help]"
    Write-Host "无参数      预览模式，仅显示将要执行的操作"
    Write-Host "-Force     执行清理，但会逐项确认"
    Write-Host "-Yes       跳过确认，直接全量清理"
    Write-Host "-Help      显示此帮助信息"
    exit 0
}

# ---- 检查 Docker ----
function Test-Docker {
    try {
        docker info | Out-Null
        if ($LASTEXITCODE -ne 0) { throw "Docker daemon not running" }
    } catch {
        Write-Danger "Docker 未运行或未安装"
        exit 1
    }
}
Test-Docker

# ============================================================
# 第一阶段：资源盘点（始终执行）
# ============================================================
Write-Host ""
Write-Host "+============================================+" -ForegroundColor Red
Write-Host "|   CareerAgent Docker 全量清理工具          |" -ForegroundColor Red
Write-Host "+============================================+" -ForegroundColor Red
Write-Header "资源盘点"

# 容器
$containers = docker ps -a --filter "label=com.docker.compose.project=$ProjectName" -q 2>$null
if ($containers) {
    $count = ($containers | Measure-Object).Count
    Write-Step "发现 $count 个本项目容器"
    docker ps -a --filter "label=com.docker.compose.project=$ProjectName" --format "    -> {{.Names}} ({{.Status}})"
} else {
    Write-Warn "无运行/停止的项目容器"
}
Write-Host ""

# 命名卷
$volExists = 0
foreach ($vol in $NamedVolumes) {
    docker volume inspect $vol 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Step "数据卷: $vol"
        $volExists++
    }
}
if ($volExists -eq 0) { Write-Warn "无项目命名卷" }
Write-Host ""

# 构建镜像
$imgFound = 0
foreach ($img in $BuiltImages) {
    $imgTag = if ($img -notmatch ":") { "${img}:latest" } else { $img }
    docker image inspect $imgTag 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) {
        $sizeInfo = docker image inspect $imgTag --format "{{.Size}}" 2>$null
        if ($sizeInfo -match '^\d+$') {
            $sizeMB = [math]::Round([long]$sizeInfo / 1MB, 1)
            Write-Step "构建镜像: $imgTag (~${sizeMB} MB)"
        } else {
            Write-Step "构建镜像: $imgTag"
        }
        $imgFound++
    }
}
if ($imgFound -eq 0) { Write-Warn "无项目构建镜像" }
Write-Host ""

# 依赖基础镜像
$depFound = 0
foreach ($img in $DependencyImages) {
    docker image inspect $img 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) {
        $sizeInfo = docker image inspect $img --format "{{.Size}}" 2>$null
        if ($sizeInfo -match '^\d+$') {
            $sizeMB = [math]::Round([long]$sizeInfo / 1MB, 1)
            Write-Step "依赖镜像: $img (~${sizeMB} MB)"
        } else {
            Write-Step "依赖镜像: $img"
        }
        $depFound++
    }
}
if ($depFound -eq 0) { Write-Warn "无项目依赖镜像" }
Write-Host ""

# 网络
docker network inspect $NetworkName 2>$null | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Step "自定义网络: $NetworkName"
} else {
    Write-Warn "无自定义网络"
}
Write-Host ""

# 构建缓存
try {
    $cacheOutput = docker builder df 2>$null | Select-String "Shared space"
    if ($cacheOutput) {
        $cacheSize = ($cacheOutput -split '\s+')[-1]
        Write-Step "Docker 构建缓存占用: $cacheSize"
    }
} catch {}
Write-Host ""

# 悬空镜像
$dangling = docker images -f "dangling=true" -q 2>$null
if ($dangling) {
    $danglingCount = ($dangling | Measure-Object).Count
    Write-Step "悬空镜像 (dangling): $danglingCount 个"
} else {
    Write-Warn "无悬空镜像"
}
Write-Host ""

# ============================================================
# 判断模式
# ============================================================
if (-not $Force -and -not $Yes) {
    Write-Host "以上为预览模式。要实际执行清理，请运行:" -ForegroundColor Yellow
    Write-Host "  .\scripts\cleanup-docker.ps1 -Force   (逐项确认)" -ForegroundColor Cyan
    Write-Host "  .\scripts\cleanup-docker.ps1 -Yes      (直接执行)" -ForegroundColor Cyan
    exit 0
}

if ($Force -and -not $Yes) {
    Write-Host "警告：以下操作将永久删除所有数据库数据和构建产物！" -ForegroundColor Red
    $answer = Read-Host "`n是否继续？(yes/no)"
    if ($answer -ne "yes") {
        Write-Host "已取消。"
        exit 0
    }
}

# ============================================================
# 第二阶段：执行清理
# ============================================================

# 步骤 1: 停止并移除容器
Write-Header "步骤 1/7: 停止并移除容器"
try {
    docker compose -f $ComposeFile down --remove-orphans 2>$null | Out-Null
    Write-Step "docker compose down 完成"
} catch {
    $orphanContainers = docker ps -a --filter "label=com.docker.compose.project=$ProjectName" -q 2>$null
    if ($orphanContainers) {
        docker rm -f $orphanContainers 2>$null | Out-Null
        Write-Step "手动移除孤立容器完成"
    } else {
        Write-Warn "无容器需要清理"
    }
}
Write-Host " "

# 步骤 2: 移除命名卷
Write-Header "步骤 2/7: 移除命名数据卷（将永久删除数据库数据！）"
Write-Step "🔄 强制停止所有相关容器和进程..."
$projContainers = docker ps -a --filter "label=com.docker.compose.project=$ProjectName" -q 2>$null
if ($projContainers) { docker rm -f $projContainers 2>$null | Out-Null }

foreach ($vol in $NamedVolumes) {
    $volContainers = docker ps -a --filter "volume=$vol" --format "{{.Names}}" 2>$null
    if ($volContainers) {
        Write-Step "🛑 停止使用卷 $vol 的容器"
        docker rm -f $volContainers 2>$null | Out-Null
    }
}
# 等待 Docker 释放卷引用（对齐 .sh 逻辑）
Start-Sleep -Seconds 2

foreach ($vol in $NamedVolumes) {
    docker volume inspect $vol 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) {
        docker volume rm $vol 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) { Write-Step "已删除卷: $vol" }
        else { Write-Warn "无法移除卷 $vol (可能仍有引用)" }
    }
}
Write-Host ""

# 步骤 3: 移除项目构建镜像
Write-Header "步骤 3/7: 移除项目构建镜像"
foreach ($img in $BuiltImages) {
    foreach ($tag in @($img, $img.TrimEnd(":latest"))) {
        docker image inspect $tag 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) {
            docker rmi $tag 2>$null | Out-Null
            if ($LASTEXITCODE -eq 0) { Write-Step "已删除: $tag" }
        }
    }
}
$noneImages = docker images -f "dangling=true" -q 2>$null
if ($noneImages) {
    docker rmi $noneImages 2>$null | Out-Null
    Write-Step "已清理悬空构建镜像"
}
Write-Host ""

# 步骤 4: 移除依赖基础镜像
Write-Header "步骤 4/7: 移除依赖基础镜像"
$depRemoved = 0
foreach ($img in $DependencyImages) {
    docker image inspect $img 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) {
        docker rmi $img 2>$null | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Step "已删除: $img"
        } else {
            Write-Warn "删除失败(可能被其他项目使用): $img"
        }
        $depRemoved++
    }
}
if ($depRemoved -eq 0) { Write-Warn "无依赖基础镜像需要清理" }
Write-Host ""

# 步骤 5: 移除自定义网络
Write-Header "步骤 5/7: 移除自定义网络"
docker network inspect $NetworkName 2>$null | Out-Null
if ($LASTEXITCODE -eq 0) {
    docker network rm $NetworkName 2>$null | Out-Null
    Write-Step "已删除网络: $NetworkName"
} else {
    Write-Warn "网络不存在，跳过"
}
Write-Host ""

# 步骤 6: 清理 Docker 构建缓存
Write-Header "步骤 6/7: 清理 Docker 构建缓存"
docker builder prune -af 2>$null | Out-Null
Write-Step "builder prune 完成"
Write-Host ""

# 步骤 7: 清理悬空镜像和 buildx 缓存
Write-Header "步骤 7/7: 清理悬空镜像与未使用资源"
docker image prune -af 2>$null | Out-Null
Write-Step "image prune 完成"
docker buildx prune -af 2>$null | Out-Null
Write-Host ""

# 最终报告
Write-Header "清理完成"
$remainingContainers = docker ps -a --filter "label=com.docker.compose.project=$ProjectName" -q 2>$null
Write-Step "剩余容器: $($remainingContainers.Count) 个"

$remainingVols = 0
foreach ($vol in $NamedVolumes) {
    docker volume inspect $vol 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) { $remainingVols++ }
}
Write-Step "剩余项目卷: $remainingVols 个"

Write-Step "Docker 磁盘占用:"
docker system df 2>$null | ForEach-Object {
    if ($_ -match '(Type|REPO|image|container|volume|build|cache)') {
        Write-Host "    $_" -ForegroundColor Gray
    }
}