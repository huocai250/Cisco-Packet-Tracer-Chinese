#!/usr/bin/env bash
# Cisco Packet Tracer 简体中文汉化包 - 安装脚本（macOS / Linux）
# 用法： sudo bash scripts/install.sh ["/path/to/Packet Tracer 9.0.1/languages"]
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
dist_dir="$repo_root/dist"

if [[ ! -f "$dist_dir/Chinese_chi.ptl" ]]; then
    echo "找不到 $dist_dir/Chinese_chi.ptl" >&2
    exit 1
fi

target="${1:-}"
if [[ -z "$target" ]]; then
    for candidate in \
        "/Applications/Cisco Packet Tracer 9.0.1.app/Contents/Resources/languages" \
        "/Applications/Cisco Packet Tracer.app/Contents/Resources/languages" \
        "/opt/pt/languages" \
        "$HOME/.local/share/Cisco Packet Tracer 9.0.1/languages"
    do
        if [[ -d "$candidate" ]]; then target="$candidate"; break; fi
    done
fi

if [[ -z "$target" || ! -d "$target" ]]; then
    echo "没找到 languages 目录，请手动指定，例如：" >&2
    echo "  sudo bash scripts/install.sh \"/Applications/Cisco Packet Tracer 9.0.1.app/Contents/Resources/languages\"" >&2
    exit 1
fi

echo "语言包来源：$dist_dir"
echo "安装目标  ：$target"

for f in Chinese_chi.ptl Chinese_chi.ts; do
    [[ -f "$dist_dir/$f" ]] || continue
    if [[ -w "$target" ]]; then
        cp -f "$dist_dir/$f" "$target/$f"
    else
        sudo cp -f "$dist_dir/$f" "$target/$f"
    fi
    echo "  已复制 $f"
done

cat <<'EOF'

安装完成。接下来：
  1. 完全退出并重新启动 Packet Tracer
  2. Options -> Preferences -> Interface -> Language 选择 Chinese
  3. 再次重启 Packet Tracer 生效

提示：languages 目录里请只保留一个中文 .ptl。
EOF
