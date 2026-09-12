#!/bin/bash
{
	#//////////////////////////////////////////////////////////////////
	# MitraOS V.1 (Apollo) - Interactive Bash Shell Integration
	# Founder: Qomaruddin Djamal
	# Company: Citra Media Technology & Mitra Utama Group
	# Location: /etc/bashrc.d/mitra.bash
	#//////////////////////////////////////////////////////////////////

	# Only run in interactive terminal shells
	[[ -t 0 && $- == *'i'* ]] || return 0

	# Ensure MitraOS paths are in PATH
	export PATH="/opt/mitraos/bin:/boot/mitraos:/boot/apollo:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

	# Useful productivity aliases
	alias mitra='mitra'
	alias launcher='mitra launcher'
	alias preferences='mitra preferences'
	alias snap='mitra snap'
	alias desktop='mitra desktop'
	alias assist='mitra asisten'
	alias antigravity='mitra antigravity'
	alias banner='mitra banner'
	alias ll='ls -alF --color=auto'
	alias la='ls -A --color=auto'
	alias l='ls -CF --color=auto'

	# Starship-style prompt
	PS1='\[\e[1;38;5;45m\]mitraOS\[\e[0m\]:\[\e[1;38;5;208m\]\w\[\e[0m\]\$ '
}
