# CODER-OS .zshrc

# History
HISTFILE=~/.zsh_history
HISTSIZE=10000
SAVEHIST=10000
setopt appendhistory sharehistory incappendhistory

# Modern Aliases
alias ls='eza --icons'
alias ll='eza -la --icons'
alias lt='eza --tree --level=2 --icons'
alias cat='bat --paging=never'
alias lg='lazygit'
alias ld='lazydocker'
alias top='btop'
alias v='nvim'
alias vim='nvim'
alias setup='coder-setup'
alias install-os='coder-setup'

# Prompt
if command -v starship &> /dev/null; then
    eval "$(starship init zsh)"
fi

# Fastfetch greeting
if [[ -o interactive ]] && command -v fastfetch &> /dev/null; then
    fastfetch
fi
