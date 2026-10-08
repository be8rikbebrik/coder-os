#!/usr/bin/env bash
# CODER-OS archiso profile definition

iso_name="coder-os"
iso_label="CODEROS_$(date +%Y%m)"
iso_publisher="CODER-OS Project <https://github.com/coder-os>"
iso_application="CODER-OS Linux Live & Installation Media"
iso_version="$(date +%Y.%m.%d)"
install_dir="coderos"
buildmodes=('iso')
bootmodes=(
    'bios.syslinux.mbr'
    'bios.syslinux.eltorito'
    'uefi-ia32.systemd-boot.esp'
    'uefi-x64.systemd-boot.esp'
    'uefi-ia32.systemd-boot.eltorito'
    'uefi-x64.systemd-boot.eltorito'
)
arch="x86_64"
pacman_conf="pacman.conf"
airootfs_image_type="squashfs"
airootfs_image_tool_options=('-comp' 'zstd')
bootstrap_tarball_compression=('zstd' '-c' '-T0' '--auto-threads=logical')
file_permissions=(
    ["/etc/shadow"]="0:0:0400"
    ["/etc/gshadow"]="0:0:0400"
    ["/etc/sudoers.d"]="0:0:0750"
    ["/etc/sudoers.d/coderos"]="0:0:0440"
    ["/root"]="0:0:0750"
    ["/root/.automated_script.sh"]="0:0:0755"
    ["/usr/local/bin/choose-mirror"]="0:0:0755"
    ["/usr/bin/coder-setup"]="0:0:0755"
    ["/usr/bin/coder-install"]="0:0:0755"
    ["/usr/bin/coder-postinstall"]="0:0:0755"
)
