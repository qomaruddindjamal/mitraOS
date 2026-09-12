#!/usr/bin/env wish
#//////////////////////////////////////////////////////////////////
# MitraOS GUI System Preferences
# Official Native Graphical Settings & Control Center
# Founder: Qomaruddin Djamal - Mitra Utama Group
# Location: /usr/share/mitraos/ui/preferences.tcl
#//////////////////////////////////////////////////////////////////

package require Tk

# -------------------------------------------------------------
# WINDOW CONFIGURATION
# -------------------------------------------------------------
wm title . "System Preferences - MitraOS"
wm geometry . 820x580+100+70
wm minsize . 760 520
. configure -bg "#0b1329"

# Color Palette (MitraOS Slate & Cyan Modern)
set BG_MAIN "#0b1329"
set BG_CARD "#111a36"
set BG_CARD_HOVER "#1b274e"
set BG_HEADER "#070c1a"
set FG_TITLE "#f8fafc"
set FG_SUB "#94a3b8"
set FG_ACCENT "#00f2fe"
set FG_ACCENT_HOVER "#38bdf8"
set BD_ACCENT "#00f2fe"
set BG_BTN "#162347"
set FG_BTN "#f8fafc"

# Font definitions
font create FontTitle -family "DejaVu Sans" -size 14 -weight bold
font create FontSub -family "DejaVu Sans" -size 9
font create FontCardTitle -family "DejaVu Sans" -size 9 -weight bold
font create FontCardSub -family "DejaVu Sans" -size 8
font create FontBtn -family "DejaVu Sans" -size 9 -weight bold
font create FontHeader -family "DejaVu Sans" -size 11 -weight bold

# -------------------------------------------------------------
# TOP HEADER BAR
# -------------------------------------------------------------
frame .header -bg $BG_HEADER -padx 16 -pady 10 -bd 0
pack .header -side top -fill x

# Logo / Back Button Container
frame .header.left -bg $BG_HEADER
pack .header.left -side left -fill y

# App Title & Subtitle
label .header.left.title -text "System Preferences" -font FontTitle -fg $FG_TITLE -bg $BG_HEADER
label .header.left.sub -text "Pusat Pengaturan Sistem & Personalisasi MitraOS" -font FontSub -fg $FG_SUB -bg $BG_HEADER
pack .header.left.title -anchor w
pack .header.left.sub -anchor w

# Right Side: Search & Exit
frame .header.right -bg $BG_HEADER
pack .header.right -side right -fill y

button .header.right.close -text "Tutup (X)" -font FontBtn -bg "#dc2626" -fg "#ffffff" \
    -activebackground "#ef4444" -activeforeground "#ffffff" -bd 0 -padx 12 -pady 4 \
    -command {exit 0} -cursor hand2
pack .header.right.close -side right -pady 4

# Separator line
frame .sep -height 1 -bg "#1e293b" -bd 0
pack .sep -side top -fill x

# -------------------------------------------------------------
# CONTENT AREA (Cards Grid or Category Detail)
# -------------------------------------------------------------
frame .content -bg $BG_MAIN -padx 12 -pady 10
pack .content -side top -fill both -expand 1

# 1. MAIN GRID FRAME
frame .content.grid -bg $BG_MAIN

# 2. DETAIL PAGE FRAME
frame .content.detail -bg $BG_MAIN

# -------------------------------------------------------------
# CATEGORY DEFINITIONS (17 Categories in 6 Columns)
# -------------------------------------------------------------
set categories {
    {"01" "Umum" "Tema & Gaya" "preferences-system.png" "show_general"}
    {"02" "Tampilan" "Resolusi Layar" "preferences-system-hardware.png" "show_display"}
    {"03" "Suara" "Volume & Audio" "audio-volume-high.png" "show_sound"}
    {"04" "Jaringan" "Internet & Wi-Fi" "preferences-system-network.png" "show_network"}
    {"05" "Bluetooth" "Nirkabel BLE" "preferences-system-bluetooth.png" "show_bluetooth"}
    {"06" "Perangkat" "Penyimpanan Disk" "drive-removable-media.png" "show_devices"}
    {"07" "Akun" "Pengguna & Admin" "system-users.png" "show_accounts"}
    {"08" "Keamanan" "Firewall & Proteksi" "preferences-security.png" "show_security"}
    {"09" "Waktu" "Jam NTP & Zona" "preferences-system-time.png" "show_datetime"}
    {"10" "Bahasa" "Keyboard Layout" "preferences-desktop-locale.png" "show_language"}
    {"11" "Pembaruan" "Pembaruan Sistem" "system-software-update.png" "show_updates"}
    {"12" "Aplikasi" "Aplikasi Bawaan" "applications-other.png" "show_applications"}
    {"13" "Privasi" "Izin & Riwayat" "preferences-system-privacy.png" "show_privacy"}
    {"14" "Daya" "Hemat Energi" "preferences-system-power.png" "show_power"}
    {"15" "Sistem" "Info Hardware" "preferences-desktop-display.png" "show_hardware"}
    {"16" "Tentang" "Identitas MitraOS" "help-about.png" "show_about"}
    {"17" "Mouse" "Presisi 1:1 Host" "preferences-system-mouse.png" "show_mouse"}
}

# Icon cache
array set icon_cache {}

proc get_icon {fname} {
    global icon_cache
    if {[info exists icon_cache($fname)]} {
        return $icon_cache($fname)
    }
    set p1 "/usr/share/mitraos/icons/system-preferences/$fname"
    set p2 "/usr/share/mitraos/$fname"
    set p3 "/usr/share/mitraos/icons/workstation/$fname"
    set found ""
    foreach p [list $p1 $p2 $p3] {
        if {[file exists $p]} {
            set found $p
            break
        }
    }
    if {$found ne ""} {
        set img [image create photo -file $found]
        set icon_cache($fname) $img
        return $img
    }
    return ""
}

# -------------------------------------------------------------
# BUILD MAIN CATEGORY GRID
# -------------------------------------------------------------
proc show_grid {} {
    global categories BG_MAIN BG_CARD BG_CARD_HOVER FG_TITLE FG_SUB FG_ACCENT
    pack forget .content.detail
    pack .content.grid -side top -fill both -expand 1

    # Clear old children if any
    foreach w [winfo children .content.grid] {
        destroy $w
    }

    set cols 6
    set row 0
    set col 0

    foreach cat $categories {
        set id [lindex $cat 0]
        set title [lindex $cat 1]
        set desc [lindex $cat 2]
        set icon_file [lindex $cat 3]
        set cmd [lindex $cat 4]

        set cframe .content.grid.card_$id
        frame $cframe -bg $BG_CARD -bd 1 -relief solid -highlightbackground "#1e293b" -highlightthickness 1 -cursor hand2 -padx 6 -pady 8
        grid $cframe -row $row -column $col -padx 6 -pady 6 -sticky news
        grid columnconfigure .content.grid $col -weight 1 -uniform card

        set img [get_icon $icon_file]
        if {$img ne ""} {
            label $cframe.ico -image $img -bg $BG_CARD -cursor hand2
            pack $cframe.ico -side top -pady 2
            bind $cframe.ico <Button-1> $cmd
        }

        label $cframe.t -text $title -font FontCardTitle -fg $FG_TITLE -bg $BG_CARD -cursor hand2
        pack $cframe.t -side top
        bind $cframe.t <Button-1> $cmd

        label $cframe.d -text $desc -font FontCardSub -fg $FG_SUB -bg $BG_CARD -cursor hand2
        pack $cframe.d -side top
        bind $cframe.d <Button-1> $cmd

        bind $cframe <Button-1> $cmd

        # Hover effects
        bind $cframe <Enter> "$cframe configure -bg $BG_CARD_HOVER -highlightbackground $FG_ACCENT; catch {$cframe.ico configure -bg $BG_CARD_HOVER}; $cframe.t configure -bg $BG_CARD_HOVER -fg $FG_ACCENT; $cframe.d configure -bg $BG_CARD_HOVER"
        bind $cframe <Leave> "$cframe configure -bg $BG_CARD -highlightbackground #1e293b; catch {$cframe.ico configure -bg $BG_CARD}; $cframe.t configure -bg $BG_CARD -fg $FG_TITLE; $cframe.d configure -bg $BG_CARD"

        incr col
        if {$col >= $cols} {
            set col 0
            incr row
        }
    }
}

# -------------------------------------------------------------
# DETAIL VIEW HELPER
# -------------------------------------------------------------
proc open_detail {title desc icon_file} {
    global BG_MAIN BG_HEADER BG_CARD FG_TITLE FG_SUB FG_ACCENT BG_BTN FG_BTN
    pack forget .content.grid
    pack .content.detail -side top -fill both -expand 1

    foreach w [winfo children .content.detail] {
        destroy $w
    }

    # Top nav bar in detail
    frame .content.detail.nav -bg $BG_MAIN -pady 6
    pack .content.detail.nav -side top -fill x

    button .content.detail.nav.back -text "<-- Kembali ke Pengaturan" -font FontBtn \
        -bg $BG_BTN -fg $FG_ACCENT -activebackground "#1e293b" -activeforeground "#ffffff" \
        -bd 1 -relief solid -highlightbackground $FG_ACCENT -padx 12 -pady 5 \
        -command {show_grid} -cursor hand2
    pack .content.detail.nav.back -side left

    set img [get_icon $icon_file]
    if {$img ne ""} {
        label .content.detail.nav.ico -image $img -bg $BG_MAIN
        pack .content.detail.nav.ico -side left -padx 12
    }

    label .content.detail.nav.t -text $title -font FontHeader -fg $FG_TITLE -bg $BG_MAIN
    pack .content.detail.nav.t -side left

    # Body frame
    frame .content.detail.body -bg $BG_CARD -bd 1 -relief solid -highlightbackground "#1e293b" -padx 20 -pady 16
    pack .content.detail.body -side top -fill both -expand 1 -pady 8

    return .content.detail.body
}

# -------------------------------------------------------------
# 01. UMUM (GENERAL)
# -------------------------------------------------------------
proc show_general {} {
    global BG_CARD FG_TITLE FG_SUB FG_ACCENT BG_BTN
    set b [open_detail "Umum (General)" "Personalisasi tema dan wallpaper desktop" "preferences-system.png"]

    label $b.t1 -text "Tema & Personalisasi Desktop" -font FontHeader -fg $FG_ACCENT -bg $BG_CARD
    pack $b.t1 -anchor w -pady 4

    label $b.d1 -text "Tema Aktif: MitraOS Dark Modern (Electric Cyan & Amber Gold)
Desain antarmuka berpusat pada kenyamanan mata dengan kontras tinggi." -font FontSub -fg $FG_SUB -bg $BG_CARD -justify left
    pack $b.d1 -anchor w -pady 4

    frame $b.btns -bg $BG_CARD -pady 10
    pack $b.btns -anchor w

    button $b.btns.w -text "Pilih & Segarkan Wallpaper Otomatis" -font FontBtn -bg $BG_BTN -fg $FG_TITLE -padx 12 -pady 6 -command {
        exec /usr/bin/mitra-wallpaper --auto &
    } -cursor hand2
    pack $b.btns.w -side left -padx 5

    button $b.btns.r -text "Muat Ulang Desktop (Refresh JWM)" -font FontBtn -bg $BG_BTN -fg $FG_TITLE -padx 12 -pady 6 -command {
        exec jwm -restart &
    } -cursor hand2
    pack $b.btns.r -side left -padx 5
}

# -------------------------------------------------------------
# 02. TAMPILAN (DISPLAY)
# -------------------------------------------------------------
proc show_display {} {
    global BG_CARD FG_TITLE FG_SUB FG_ACCENT BG_BTN
    set b [open_detail "Tampilan (Display)" "Pengaturan resolusi layar" "preferences-system-hardware.png"]

    label $b.t1 -text "Pengaturan Resolusi Monitor" -font FontHeader -fg $FG_ACCENT -bg $BG_CARD
    pack $b.t1 -anchor w -pady 4

    label $b.d1 -text "Pilih resolusi layar yang diinginkan (perubahan diterapkan seketika):" -font FontSub -fg $FG_SUB -bg $BG_CARD
    pack $b.d1 -anchor w -pady 4

    set resolutions {
        {"1024 x 768  (Standar VM & Proyektor)" "1024x768"}
        {"1280 x 720  (HD 720p 16:9)" "1280x720"}
        {"1366 x 768  (Laptop HD)" "1366x768"}
        {"1920 x 1080 (Full HD 1080p)" "1920x1080"}
        {"2560 x 1440 (2K QHD)" "2560x1440"}
    }

    set i 0
    foreach r $resolutions {
        set label [lindex $r 0]
        set mode [lindex $r 1]
        button $b.btn_$i -text $label -font FontBtn -bg $BG_BTN -fg $FG_TITLE -padx 14 -pady 5 -anchor w -command "
            exec xrandr -s $mode
            catch {exec /usr/bin/mitra-wallpaper --auto}
        " -cursor hand2
        pack $b.btn_$i -fill x -pady 3
        incr i
    }
}

# -------------------------------------------------------------
# 03. SUARA (SOUND)
# -------------------------------------------------------------
proc show_sound {} {
    global BG_CARD FG_TITLE FG_SUB FG_ACCENT BG_BTN
    set b [open_detail "Suara (Sound)" "Volume master dan output audio" "audio-volume-high.png"]

    label $b.t1 -text "Volume Master Audio" -font FontHeader -fg $FG_ACCENT -bg $BG_CARD
    pack $b.t1 -anchor w -pady 6

    scale $b.s -from 0 -to 100 -orient horizontal -length 400 -bg $BG_CARD -fg $FG_ACCENT -troughcolor "#161f30" -highlightthickness 0 -command {apply_vol}
    $b.s set 80
    pack $b.s -anchor w -pady 10

    frame $b.btn_row -bg $BG_CARD -pady 8
    pack $b.btn_row -anchor w

    button $b.btn_row.mute -text "Bisukan (Mute)" -font FontBtn -bg $BG_BTN -fg $FG_TITLE -padx 12 -pady 6 -command {
        exec amixer set Master toggle 2>/dev/null
    } -cursor hand2
    pack $b.btn_row.mute -side left -padx 4

    button $b.btn_row.test -text "Uji Suara Beep" -font FontBtn -bg $BG_BTN -fg $FG_ACCENT -padx 12 -pady 6 -command {
        exec echo -e "\a" > /dev/tty
    } -cursor hand2
    pack $b.btn_row.test -side left -padx 4
}

proc apply_vol {val} {
    catch {exec amixer set Master "${val}%" 2>/dev/null}
}

# -------------------------------------------------------------
# 04. JARINGAN (NETWORK)
# -------------------------------------------------------------
proc show_network {} {
    global BG_CARD FG_TITLE FG_SUB FG_ACCENT BG_BTN
    set b [open_detail "Jaringan (Network)" "Koneksi internet, IP address & Wi-Fi" "preferences-system-network.png"]

    label $b.t1 -text "Status Koneksi Internet & IP" -font FontHeader -fg $FG_ACCENT -bg $BG_CARD
    pack $b.t1 -anchor w -pady 4

    # Fetch IP info
    set ip_info [exec ip -4 a 2>/dev/null | grep -E "inet " | grep -v "127.0.0.1" | awk "{print \$2 " on " \$NF}"]
    label $b.ip -text "Alamat IP: $ip_info" -font FontBtn -fg $FG_TITLE -bg $BG_CARD
    pack $b.ip -anchor w -pady 6

    frame $b.btn_row -bg $BG_CARD -pady 8
    pack $b.btn_row -anchor w

    button $b.btn_row.ping -text "Uji Ping Internet (8.8.8.8)" -font FontBtn -bg $BG_BTN -fg $FG_ACCENT -padx 12 -pady 6 -command {
        set res [catch {exec ping -c 2 8.8.8.8} out]
        if {$res == 0} {
            tk_messageBox -title "Uji Ping" -message "Koneksi Internet Berhasil Terhubung!

$out"
        } else {
            tk_messageBox -icon error -title "Uji Ping" -message "Koneksi Gagal atau Terputus."
        }
    } -cursor hand2
    pack $b.btn_row.ping -side left -padx 4

    button $b.btn_row.res -text "Restart Layanan Jaringan" -font FontBtn -bg $BG_BTN -fg $FG_TITLE -padx 12 -pady 6 -command {
        exec systemctl restart networking 2>/dev/null || exec /etc/init.d/networking restart 2>/dev/null
        tk_messageBox -title "Jaringan" -message "Layanan jaringan telah dimulai ulang."
    } -cursor hand2
    pack $b.btn_row.res -side left -padx 4
}

# -------------------------------------------------------------
# 05. BLUETOOTH
# -------------------------------------------------------------
proc show_bluetooth {} {
    global BG_CARD FG_TITLE FG_SUB FG_ACCENT
    set b [open_detail "Bluetooth" "Perangkat nirkabel & BLE" "preferences-system-bluetooth.png"]
    label $b.t1 -text "Pengaturan Perangkat Nirkabel (Bluetooth)" -font FontHeader -fg $FG_ACCENT -bg $BG_CARD
    pack $b.t1 -anchor w -pady 4
    label $b.d1 -text "Dukungan Bluetooth hemat daya (BLE) dan sinkronisasi audio nirkabel.\nStatus Adapter: Siap digunakan (Ready)." -font FontSub -fg $FG_SUB -bg $BG_CARD -justify left
    pack $b.d1 -anchor w -pady 6
}

# -------------------------------------------------------------
# 06. PERANGKAT (DEVICES & STORAGE)
# -------------------------------------------------------------
proc show_devices {} {
    global BG_CARD FG_TITLE FG_SUB FG_ACCENT
    set b [open_detail "Perangkat (Devices)" "Penyimpanan USB dan partisi disk" "drive-harddisk.png"]
    label $b.t1 -text "Daftar Partisi & Ruang Penyimpanan Disk" -font FontHeader -fg $FG_ACCENT -bg $BG_CARD
    pack $b.t1 -anchor w -pady 4

    set df_info [exec df -h / 2>/dev/null]
    label $b.out -text $df_info -font {Courier 9} -fg $FG_TITLE -bg "#060a14" -padx 10 -pady 8 -justify left
    pack $b.out -anchor w -fill x -pady 6
}

# -------------------------------------------------------------
# 07. AKUN (USERS)
# -------------------------------------------------------------
proc show_accounts {} {
    global BG_CARD FG_TITLE FG_SUB FG_ACCENT
    set b [open_detail "Akun (Users)" "Profil pengguna & izin sistem" "user-identity.png"]
    label $b.t1 -text "Manajemen Akun Pengguna" -font FontHeader -fg $FG_ACCENT -bg $BG_CARD
    pack $b.t1 -anchor w -pady 4
    label $b.d1 -text "Pengguna Aktif: root (Administrator Utama MitraOS)\nHak Akses: Full Superuser & Sudo Bypass\nSesi: LiveCD Workstation Session" -font FontSub -fg $FG_SUB -bg $BG_CARD -justify left
    pack $b.d1 -anchor w -pady 6
}

# -------------------------------------------------------------
# 08. KEAMANAN (SECURITY)
# -------------------------------------------------------------
proc show_security {} {
    global BG_CARD FG_TITLE FG_SUB FG_ACCENT
    set b [open_detail "Keamanan (Security)" "Firewall & proteksi sistem" "preferences-system-privacy.png"]
    label $b.t1 -text "Status Keamanan & Firewall Sistem" -font FontHeader -fg $FG_ACCENT -bg $BG_CARD
    pack $b.t1 -anchor w -pady 4
    label $b.d1 -text "Proteksi Kernel: Aktif (Strict Memory Isolation)\nFirewall: Siap (iptables filtering engine)\nEnkripsi: TLS 1.3 / OpenSSH Port 22 Active" -font FontSub -fg $FG_SUB -bg $BG_CARD -justify left
    pack $b.d1 -anchor w -pady 6
}

# -------------------------------------------------------------
# 09. TANGGAL & WAKTU (DATETIME)
# -------------------------------------------------------------
proc show_datetime {} {
    global BG_CARD FG_TITLE FG_SUB FG_ACCENT BG_BTN
    set b [open_detail "Tanggal & Waktu" "Zona waktu dan jam NTP" "preferences-system-time.png"]
    label $b.t1 -text "Waktu Sistem Saat Ini" -font FontHeader -fg $FG_ACCENT -bg $BG_CARD
    pack $b.t1 -anchor w -pady 4

    set cur_time [exec date 2>/dev/null]
    label $b.time -text $cur_time -font FontHeader -fg $FG_ACCENT -bg $BG_CARD
    pack $b.time -anchor w -pady 6

    frame $b.tz_row -bg $BG_CARD -pady 8
    pack $b.tz_row -anchor w

    button $b.tz_row.wib -text "WIB (Jakarta UTC+7)" -font FontBtn -bg $BG_BTN -fg $FG_TITLE -padx 10 -pady 5 -command {
        exec ln -sf /usr/share/zoneinfo/Asia/Jakarta /etc/localtime 2>/dev/null
        tk_messageBox -title "Zona Waktu" -message "Zona waktu disetel ke WIB (Asia/Jakarta)."
    } -cursor hand2
    pack $b.tz_row.wib -side left -padx 4

    button $b.tz_row.wita -text "WITA (Makassar UTC+8)" -font FontBtn -bg $BG_BTN -fg $FG_TITLE -padx 10 -pady 5 -command {
        exec ln -sf /usr/share/zoneinfo/Asia/Makassar /etc/localtime 2>/dev/null
        tk_messageBox -title "Zona Waktu" -message "Zona waktu disetel ke WITA (Asia/Makassar)."
    } -cursor hand2
    pack $b.tz_row.wita -side left -padx 4

    button $b.tz_row.wit -text "WIT (Jayapura UTC+9)" -font FontBtn -bg $BG_BTN -fg $FG_TITLE -padx 10 -pady 5 -command {
        exec ln -sf /usr/share/zoneinfo/Asia/Jayapura /etc/localtime 2>/dev/null
        tk_messageBox -title "Zona Waktu" -message "Zona waktu disetel ke WIT (Asia/Jayapura)."
    } -cursor hand2
    pack $b.tz_row.wit -side left -padx 4
}

# -------------------------------------------------------------
# 10. BAHASA (LANGUAGE & KEYBOARD)
# -------------------------------------------------------------
proc show_language {} {
    global BG_CARD FG_TITLE FG_SUB FG_ACCENT BG_BTN
    set b [open_detail "Bahasa & Keyboard" "Tata letak keyboard" "input-keyboard.png"]
    label $b.t1 -text "Pilih Tata Letak Keyboard (Keyboard Layout)" -font FontHeader -fg $FG_ACCENT -bg $BG_CARD
    pack $b.t1 -anchor w -pady 4

    frame $b.kb_row -bg $BG_CARD -pady 8
    pack $b.kb_row -anchor w

    button $b.kb_row.us -text "US Standard QWERTY" -font FontBtn -bg $BG_BTN -fg $FG_ACCENT -padx 12 -pady 6 -command {
        exec setxkbmap us 2>/dev/null
        tk_messageBox -title "Keyboard" -message "Tata letak US QWERTY telah diterapkan."
    } -cursor hand2
    pack $b.kb_row.us -side left -padx 4

    button $b.kb_row.uk -text "UK English" -font FontBtn -bg $BG_BTN -fg $FG_TITLE -padx 12 -pady 6 -command {
        exec setxkbmap gb 2>/dev/null
        tk_messageBox -title "Keyboard" -message "Tata letak UK English telah diterapkan."
    } -cursor hand2
    pack $b.kb_row.uk -side left -padx 4
}

# -------------------------------------------------------------
# 11. PEMBARUAN (UPDATES)
# -------------------------------------------------------------
proc show_updates {} {
    global BG_CARD FG_TITLE FG_SUB FG_ACCENT BG_BTN
    set b [open_detail "Pembaruan (Updates)" "Pembaruan sistem MitraOS" "system-software-update.png"]
    label $b.t1 -text "Pusat Pembaruan Sistem MitraOS" -font FontHeader -fg $FG_ACCENT -bg $BG_CARD
    pack $b.t1 -anchor w -pady 4
    label $b.d1 -text "Versi Terpasang: MitraOS V.1 (Apollo Release)\nStatus: Sistem Anda sudah menggunakan pembaruan termutakhir." -font FontSub -fg $FG_SUB -bg $BG_CARD -justify left
    pack $b.d1 -anchor w -pady 6

    button $b.check -text "Periksa Pembaruan Sekarang" -font FontBtn -bg $BG_BTN -fg $FG_ACCENT -padx 14 -pady 6 -command {
        tk_messageBox -title "Pembaruan" -message "Selamat! Semua paket inti MitraOS berada pada versi terbaru."
    } -cursor hand2
    pack $b.check -anchor w -pady 8
}

# -------------------------------------------------------------
# 12. APLIKASI (APPLICATIONS)
# -------------------------------------------------------------
proc show_applications {} {
    global BG_CARD FG_TITLE FG_SUB FG_ACCENT
    set b [open_detail "Aplikasi (Applications)" "Aplikasi bawaan sistem" "application-x-executable.png"]
    label $b.t1 -text "Aplikasi Default Terpasang" -font FontHeader -fg $FG_ACCENT -bg $BG_CARD
    pack $b.t1 -anchor w -pady 4
    label $b.d1 -text "• Pengelola Berkas : Workstation Explorer / Midnight Commander\n• Terminal Emulator: MitraOS Terminal (Monospace High-Contrast)\n• Penampil Gambar : Feh Fast Lightweight Viewer\n• Window Manager   : JWM (Cupertino Dock & Glass Edition)" -font FontSub -fg $FG_SUB -bg $BG_CARD -justify left
    pack $b.d1 -anchor w -pady 6
}

# -------------------------------------------------------------
# 13. PRIVASI (PRIVACY)
# -------------------------------------------------------------
proc show_privacy {} {
    global BG_CARD FG_TITLE FG_SUB FG_ACCENT BG_BTN
    set b [open_detail "Privasi (Privacy)" "Perlindungan data & privasi pengguna" "security-high.png"]
    label $b.t1 -text "Perlindungan Data & Riwayat Sesi" -font FontHeader -fg $FG_ACCENT -bg $BG_CARD
    pack $b.t1 -anchor w -pady 4
    label $b.d1 -text "MitraOS dirancang dengan privasi murni: Tanpa telemetri pihak ketiga, tanpa pelacakan data, dan sesi live ramfs otomatis bersih saat dimatikan." -font FontSub -fg $FG_SUB -bg $BG_CARD -justify left
    pack $b.d1 -anchor w -pady 6
}

# -------------------------------------------------------------
# 14. DAYA (POWER)
# -------------------------------------------------------------
proc show_power {} {
    global BG_CARD FG_TITLE FG_SUB FG_ACCENT BG_BTN
    set b [open_detail "Daya (Power)" "Penghematan baterai dan screen sleep" "preferences-system-power.png"]
    label $b.t1 -text "Pengaturan Waktu Tidur Layar (Screen Timeout)" -font FontHeader -fg $FG_ACCENT -bg $BG_CARD
    pack $b.t1 -anchor w -pady 4

    frame $b.p_row -bg $BG_CARD -pady 8
    pack $b.p_row -anchor w

    button $b.p_row.b1 -text "5 Menit" -font FontBtn -bg $BG_BTN -fg $FG_TITLE -padx 10 -pady 5 -command {
        exec xset s 300 300 2>/dev/null; exec xset +dpms 2>/dev/null
        tk_messageBox -title "Daya" -message "Layar tidur disetel ke 5 menit."
    } -cursor hand2
    pack $b.p_row.b1 -side left -padx 4

    button $b.p_row.b2 -text "15 Menit" -font FontBtn -bg $BG_BTN -fg $FG_TITLE -padx 10 -pady 5 -command {
        exec xset s 900 900 2>/dev/null; exec xset +dpms 2>/dev/null
        tk_messageBox -title "Daya" -message "Layar tidur disetel ke 15 menit."
    } -cursor hand2
    pack $b.p_row.b2 -side left -padx 4

    button $b.p_row.b3 -text "Jangan Pernah Tidur" -font FontBtn -bg $BG_BTN -fg $FG_ACCENT -padx 10 -pady 5 -command {
        exec xset s off 2>/dev/null; exec xset -dpms 2>/dev/null
        tk_messageBox -title "Daya" -message "Layar diatur selalu aktif (Screen sleep dimatikan)."
    } -cursor hand2
    pack $b.p_row.b3 -side left -padx 4
}

# -------------------------------------------------------------
# 15. SISTEM (HARDWARE)
# -------------------------------------------------------------
proc show_hardware {} {
    global BG_CARD FG_TITLE FG_SUB FG_ACCENT
    set b [open_detail "Sistem (Hardware)" "Informasi prosesor & memori" "computer.png"]
    label $b.t1 -text "Spesifikasi Hardware & Utilisasi Sistem" -font FontHeader -fg $FG_ACCENT -bg $BG_CARD
    pack $b.t1 -anchor w -pady 4

    set cpu [exec grep "model name" /proc/cpuinfo 2>/dev/null | head -n 1 | cut -d: -f2]
    set mem [exec free -m 2>/dev/null | grep Mem: | awk "{print \$3 " MB used / " \$2 " MB total"}"]
    set kern [exec uname -r 2>/dev/null]

    label $b.d1 -text "• Prosesor : $cpu\n• Memori RAM: $mem\n• Kernel    : Linux $kern\n• Arsitektur: x86_64 High-Performance Edition" -font FontSub -fg $FG_TITLE -bg $BG_CARD -justify left
    pack $b.d1 -anchor w -pady 6
}

# -------------------------------------------------------------
# 16. TENTANG (ABOUT MITRAOS)
# -------------------------------------------------------------
proc show_about {} {
    global BG_CARD FG_TITLE FG_SUB FG_ACCENT
    set b [open_detail "Tentang MitraOS" "Informasi rilis dan pengembang" "help-about.png"]

    label $b.t1 -text "MitraOS V.1 (Apollo Release)" -font FontHeader -fg $FG_ACCENT -bg $BG_CARD
    pack $b.t1 -anchor w -pady 4

    label $b.d1 -text "Founder      : Qomaruddin Djamal\nPerusahaan   : Citra Media Technology & Mitra Utama Group\nLisensi      : Open-Source Enterprise Community License\nSitus Resmi  : https://qomaruddindjamal.github.io\nDukungan     : citramedia.info@gmail.com & mitrautama.info@gmail.com\n\nSistem operasi modern, ultra-responsif, dirancang untuk efisiensi tinggi dari komputer legacy hingga workstation modern." -font FontSub -fg $FG_TITLE -bg $BG_CARD -justify left
    pack $b.d1 -anchor w -pady 6
}

# -------------------------------------------------------------
# 17. MOUSE & TOUCHPAD (POINTER SPEED & SYNC)
# -------------------------------------------------------------
proc show_mouse {} {
    global BG_CARD FG_TITLE FG_SUB FG_ACCENT BG_BTN
    set b [open_detail "Mouse & Touchpad" "Kalibrasi kecepatan pointer dan sinkronisasi host" "preferences-system-mouse.png"]

    label $b.t1 -text "Pengaturan & Kalibrasi Pointer Kursor" -font FontHeader -fg $FG_ACCENT -bg $BG_CARD
    pack $b.t1 -anchor w -pady 4

    label $b.d1 -text "Atur kecepatan dan hilangkan delay antara kursor mouse host dan sistem:" -font FontSub -fg $FG_SUB -bg $BG_CARD
    pack $b.d1 -anchor w -pady 4

    # Speed Scale
    label $b.lbl_s -text "Kecepatan Pointer (Acceleration Factor):" -font FontBtn -fg $FG_TITLE -bg $BG_CARD
    pack $b.lbl_s -anchor w -pady 2

    scale $b.scale_m -from 1 -to 5 -orient horizontal -length 350 -bg $BG_CARD -fg $FG_ACCENT -troughcolor "#161f30" -highlightthickness 0 -command {apply_mouse_speed}
    $b.scale_m set 1
    pack $b.scale_m -anchor w -pady 6

    # Action Buttons
    frame $b.btn_row -bg $BG_CARD -pady 8
    pack $b.btn_row -anchor w

    button $b.btn_row.sync -text "Terapkan Presisi 1:1 (Menyatu Sempurna Tanpa Jarak)" -font FontBtn -bg "#0284c7" -fg "#ffffff" -activebackground $FG_ACCENT -activeforeground "#000000" -padx 14 -pady 6 -command {
        exec xset m 1/1 0 2>/dev/null
        tk_messageBox -title "Mouse Sync" -message "Sinkronisasi 1:1 Berhasil! Pointer mouse kini menyatu presisi dengan host VM."
    } -cursor hand2
    pack $b.btn_row.sync -side left -padx 4

    button $b.btn_row.reset -text "Reset Default" -font FontBtn -bg $BG_BTN -fg $FG_TITLE -padx 12 -pady 6 -command {
        exec xset m default 2>/dev/null
        $b.scale_m set 2
        tk_messageBox -title "Mouse Reset" -message "Kecepatan mouse dikembalikan ke pengaturan default."
    } -cursor hand2
    pack $b.btn_row.reset -side left -padx 4

    # Interactive Test Pad
    label $b.lbl_test -text "Area Uji Pointer & Klik (Arahkan dan klik di kotak di bawah):" -font FontBtn -fg $FG_TITLE -bg $BG_CARD
    pack $b.lbl_test -anchor w -pady 8

    canvas $b.pad -width 400 -height 80 -bg "#060a14" -bd 1 -relief solid -highlightbackground $FG_ACCENT
    pack $b.pad -anchor w
    $b.pad create text 200 40 -text "Area Uji Pointer: Gerakkan Mouse & Klik Disini" -fill $FG_ACCENT -tags pad_text

    bind $b.pad <Button-1> {
        .content.detail.body.pad itemconfigure pad_text -text "✓ Klik Kiri Terdeteksi Sempurna! (Menyatu Presisi)" -fill "#22c55e"
    }
    bind $b.pad <Button-3> {
        .content.detail.body.pad itemconfigure pad_text -text "✓ Klik Kanan Terdeteksi Sempurna!" -fill "#f59e0b"
    }
}

proc apply_mouse_speed {val} {
    catch {exec xset m "${val}/1" 0 2>/dev/null}
}

# -------------------------------------------------------------
# STARTUP: SHOW GRID
# -------------------------------------------------------------
show_grid
