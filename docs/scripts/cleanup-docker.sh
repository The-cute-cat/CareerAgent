#!/bin/bash
# ============================================================
#  CareerAgent Docker Compose 全量清理脚本
#
#  用途: 清理本 Docker Compose 产生的所有容器、镜像、
#        数据卷、网络及构建缓存
#
#  使用:
#    bash ./scripts/cleanup-docker.sh           # 预览模式（显示将要执行的操作）
#    bash ./scripts/cleanup-docker.sh --force   # 执行清理（需确认）
#    bash ./scripts/cleanup-docker.sh --yes     # 跳过确认，直接执行
#
#  注意: 此操作不可逆，所有数据库数据将被永久删除！
# ============================================================

set -euo pipefail

# ---- 颜色定义 ----
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# ---- 项目常量 ----
COMPOSE_FILE="docker-compose.yml"
PROJECT_NAME="careeragent"           # Docker Compose 项目名（取自目录名）
NETWORK_NAME="career-network"

# 命名卷列表（与 docker-compose.yml 中定义一致）
NAMED_VOLUMES=(
    "career-mysql-data"
    "career-redis-data"
    "career-neo4j-data"
    "career-neo4j-logs"
    "career-rabbitmq-data"
    "career-ai-data"
    "career-ai-logs"
    "career-milvus-data"
)

# 本项目构建的镜像标签（Dockerfile 构建的，非拉取的官方镜像）
BUILT_IMAGES=(
    "careeragent-backend:latest"          # backend 服务构建产物
    "careeragent-frontend:latest"         # frontend 服务构建产物
    "careeragent-ai-service:latest"                # ai-service 服务构建产物
)

# 依赖基础镜像（docker-compose.yml 中拉取的第三方镜像，含镜像加速前缀）
DEPENDENCY_IMAGES=(
    "docker.1ms.run/mysql:8.0"
    "docker.1ms.run/redis:7-alpine"
    "docker.1ms.run/neo4j:5-community"
    "docker.1ms.run/rabbitmq:3-management-alpine"
    "docker.1ms.run/milvusdb/milvus:v2.4.14"
)

# ---- 参数解析 ----
MODE="preview"
case "${1:-}" in
    --force|-f)
        MODE="confirm"
        ;;
    --yes|-y)
        MODE="exec"
        ;;
    --help|-h)
        echo "用法: $0 [--force|--yes|--help]"
        echo "  无参数      预览模式，仅显示将要执行的操作"
        echo "  --force,-f  执行清理，但会逐项确认"
        echo "  --yes,-y    跳过确认，直接全量清理"
        exit 0
        ;;
esac

# ---- 工具函数 ----
header() {
    echo ""
    echo -e "${BOLD}${CYAN}━━━ $1 ━━━${NC}"
}

step() {
    echo -e "  ${GREEN}✔${NC} $1"
}

warn() {
    echo -e "  ${YELLOW}⚠ ${NC}$1"
}

danger() {
    echo -e "  ${RED}✘${NC} $1"
}

dry_run() {
    echo -e "  [DRY-RUN] ${CYAN}$1${NC}"
}

# 检查命令是否存在
check_docker() {
    if ! command -v docker &>/dev/null; then
        danger "Docker 未安装或不在 PATH 中"
        exit 1
    fi
    if ! docker info &>/dev/null 2>&1; then
        danger "Docker daemon 未运行"
        exit 1
    fi
}

# ============================================================
#  第一阶段：资源盘点（始终执行）
# ============================================================
inventory() {
    header "资源盘点"

    # 容器
    CONTAINERS=$(docker ps -a --filter "label=com.docker.compose.project=${PROJECT_NAME}" -q 2>/dev/null || true)
    if [[ -n "$CONTAINERS" ]]; then
        CONTAINER_COUNT=$(echo "$CONTAINERS" | wc -l | tr -d ' ')
        step "发现 ${CONTAINER_COUNT} 个本项目容器"
        docker ps -a --filter "label=com.docker.compose.project=${PROJECT_NAME}" --format "    → {{.Names}} ({{.Status}})"
    else
        warn "无运行/停止的项目容器"
    fi
    echo ""

    # 命名卷
    VOL_EXISTS=0
    for vol in "${NAMED_VOLUMES[@]}"; do
        if docker volume inspect "$vol" &>/dev/null 2>&1; then
            SIZE=$(docker volume inspect "$vol" --format '{{.Mountpoint}}' 2>/dev/null || echo "?")
            step "数据卷: $vol"
            VOL_EXISTS=$((VOL_EXISTS + 1))
        fi
    done
    if [[ "$VOL_EXISTS" -eq 0 ]]; then
        warn "无项目命名卷"
    fi
    echo ""

    # 本项目构建的镜像
    IMG_FOUND=0
    for img in "${BUILT_IMAGES[@]}"; do
        if docker image inspect "$img:latest" &>/dev/null 2>&1 \
            || docker image inspect "$img" &>/dev/null 2>&1; then
            SIZE=$(docker image inspect "$img" --format '{{.Size}}' 2>/dev/null | awk '{printf "%.1f MB", $1/1024/1024}')
            step "构建镜像: $img (~${SIZE})"
            IMG_FOUND=$((IMG_FOUND + 1))
        fi
    done

    # ai-service 镜像（可能没有固定 tag，尝试从容器推断）
    AI_IMG=$(docker inspect career-ai-service --format '{{.Config.Image}}' 2>/dev/null || echo "")
    if [[ -n "$AI_IMG" ]] && [[ "$AI_IMG" != "" ]]; then
        step "构建镜像: ai-service ($AI_IMG)"
        IMG_FOUND=$((IMG_FOUND + 1))
    fi

    if [[ "$IMG_FOUND" -eq 0 ]]; then
        warn "无项目构建镜像"
    fi

    # 依赖基础镜像
    DEP_FOUND=0
    for img in "${DEPENDENCY_IMAGES[@]}"; do
        if docker image inspect "$img" &>/dev/null 2>&1; then
            SIZE=$(docker image inspect "$img" --format '{{.Size}}' 2>/dev/null | awk '{printf "%.1f MB", $1/1024/1024}')
            step "依赖镜像: $img (~${SIZE})"
            DEP_FOUND=$((DEP_FOUND + 1))
        fi
    done
    if [[ "$DEP_FOUND" -eq 0 ]]; then
        warn "无项目依赖镜像"
    fi
    echo ""

    # 网络
    if docker network inspect "$NETWORK_NAME" &>/dev/null 2>&1; then
        step "自定义网络: $NETWORK_NAME"
    else
        warn "无自定义网络"
    fi
    echo ""

    # 构建缓存
    CACHE_DISK=$(docker builder df 2>/dev/null | grep "Shared space" | awk '{print $NF}' || echo "未知")
    step "Docker 构建缓存占用: ${CACHE_DISK}"

    # 悬空镜像
    DANGLING=$(docker images -f "dangling=true" -q 2>/dev/null | wc -l | tr -d ' ')
    if [[ "$DANGLING" -gt 0 ]]; then
        step "悬空镜像 (dangling): ${DANGLING} 个"
    else
        warn "无悬空镜像"
    fi
}

# ============================================================
#  第二阶段：执行清理
# ============================================================
do_cleanup() {

    # 1. 停止并移除容器
    header "步骤 1/7: 停止并移除容器"
    if docker compose -f "$COMPOSE_FILE" ps -q &>/dev/null 2>&1; then
        docker compose -f "$COMPOSE_FILE" down --remove-orphans 2>/dev/null \
            || docker compose -f "$COMPOSE_FILE" down
    else
        warn "docker compose 未找到运行中的服务，尝试手动清理..."
        docker rm -f $(docker ps -a --filter "label=com.docker.compose.project=${PROJECT_NAME}" -q 2>/dev/null) 2>/dev/null || true
    fi
    echo ""

    # 2. 移除命名卷
    header "步骤 2/7: 移除命名数据卷（将永久删除数据库数据！）"
    echo "  🔄 强制停止所有相关容器和进程..."
    # 停止所有相关容器（包括停止状态的）
    docker ps -a --filter "label=com.docker.compose.project=${PROJECT_NAME}" -q | xargs -r docker rm -f 2>/dev/null || true
    # 停止所有可能使用这些卷的容器
    for vol in "${NAMED_VOLUMES[@]}"; do
        # 查找使用此卷的所有容器
        containers=$(docker ps -a --filter "volume=$vol" --format "{{.Names}}" 2>/dev/null || true)
        if [[ -n "$containers" ]]; then
            echo "  🛑 停止使用卷 $vol 的容器: $containers"
            echo "$containers" | xargs -r docker rm -f 2>/dev/null || true
        fi
    done
    # 等待一下让 Docker 清理引用
    sleep 2
    for vol in "${NAMED_VOLUMES[@]}"; do
        if docker volume inspect "$vol" &>/dev/null 2>&1; then
            echo "  🗑️  移除数据卷: $vol"
            docker volume rm "$vol" 2>/dev/null || echo "  ⚠️  无法移除卷 $vol，可能仍有引用"
        fi
    done
    echo ""

    # 3. 移除本项目构建的镜像
    header "步骤 3/7: 移除项目构建镜像"
    for img in "${BUILT_IMAGES[@]}"; do
        if docker image inspect "$img:latest" &>/dev/null 2>&1; then
            docker rmi "$img:latest" 2>/dev/null || docker rmi "$img" 2>/dev/null || true
        fi
        if docker image inspect "$img" &>/dev/null 2>&1; then
            docker rmi "$img" 2>/dev/null || true
        fi
    done
    echo ""

    # 3.5 移除依赖基础镜像（docker-compose.yml 中拉取的第三方镜像）
    header "步骤 4/7: 移除依赖基础镜像"
    DEP_REMOVED=0
    for img in "${DEPENDENCY_IMAGES[@]}"; do
        if docker image inspect "$img" &>/dev/null 2>&1; then
            if docker rmi "$img" 2>/dev/null; then
                step "已删除: $img"
            else
                warn "删除失败(可能被其他项目使用): $img"
            fi
            DEP_REMOVED=$((DEP_REMOVED + 1))
        fi
    done
    if [[ "$DEP_REMOVED" -eq 0 ]]; then
        warn "无依赖基础镜像需要清理"
    fi
    echo ""

    # 5. 移除自定义网络
    header "步骤 5/7: 移除自定义网络"
    if docker network inspect "$NETWORK_NAME" &>/dev/null 2>&1; then
        docker network rm "$NETWORK_NAME"
    else
        warn "网络不存在，跳过"
    fi
    echo ""

    # 6. 清理 Docker 构建缓存
    header "步骤 6/7: 清理 Docker 构建缓存"
    docker builder prune -af
    echo ""

    # 7. 清理悬空镜像和未使用资源
    header "步骤 7/7: 清理悬空镜像与未使用资源"
    DANGLING_COUNT=$(docker images -f "dangling=true" -q 2>/dev/null | wc -l | tr -d ' ')
    if [[ "$DANGLING_COUNT" -gt 0 ]]; then
        docker image prune -af
    else
        warn "无悬空镜像需要清理"
    fi
    # 清理未使用的 buildkit 缓存
    docker buildx prune -af 2>/dev/null || true
    echo ""

    # 最终报告
    header "清理完成"
    step "剩余容器: $(docker ps -a --filter 'label=com.docker.compose.project=${PROJECT_NAME}' -q 2>/dev/null | wc -l | tr -d ' ') 个"
    step "剩余项目卷: $(printf '%s\n' "${NAMED_VOLUMES[@]}" | while read v; do docker volume inspect "$v" &>/dev/null && echo "$v"; done | wc -l | tr -d ' ') 个"
    step "Docker 磁盘占用:"
    docker system df --format "    {{.Type}}: {{.Size}}" 2>/dev/null || true
}

# ============================================================
#  主流程
# ============================================================
main() {
    check_docker

    echo ""
    echo -e "${BOLD}${RED}  ╔══════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}${RED}  ║   CareerAgent Docker 全量清理工具        ║${NC}"
    echo -e "${BOLD}${RED}  ╚══════════════════════════════════════════╝${NC}"

    inventory

    case "$MODE" in
        preview)
            echo ""
            echo -e "${YELLOW}以上为预览模式。要实际执行清理，请运行:${NC}"
            echo -e "  ${CYAN}$0 --force${NC}   （逐项确认）"
            echo -e "  ${CYAN}$0 --yes${NC}     （直接执行，无需确认）"
            ;;

        confirm)
            echo ""
            echo -e "${RED}${BOLD}⚠ 警告：以下操作将永久删除所有数据库数据和构建产物！${NC}"
            read -p "是否继续？(yes/no): " answer
            if [[ "$answer" != "yes" ]]; then
                echo "已取消。"
                exit 0
            fi
            do_cleanup
            ;;

        exec)
            do_cleanup
            ;;
    esac
}

main "$@"
