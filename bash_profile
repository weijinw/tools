#  ---------------------------------------------------------------------------
#
#  Description:  This file holds all my BASH configurations and aliases
#
#  Sections:
#  1.   Environment Configuration
#  2.   Make Terminal Better (remapping defaults and adding functionality)
#  3.   File and Folder Management
#  4.   Searching
#  5.   Process Management
#  6.   Networking
#  7.   System Operations & Information
#  8.   Web Development
#  9.   Reminders & Notes
#  
#  see http://natelandau.com/my-mac-osx-bash_profile/
#  ---------------------------------------------------------------------------

#   -------------------------------
#   1.  ENVIRONMENT CONFIGURATION
#   -------------------------------

#   Change Prompt
    export PS1="______________________________________\n| \w @ \h (\u) \n| => "
    export PS2="| => "

#   Set Paths
    export PATH=$PATH:/Users/wiwang/ws/tools/maven/bin:/build/toolchain/mac32/fortify-ssc-3.9/bin  # maven
     export PATH="/usr/local/git/bin:/usr/local/bin:/usr/local/:/usr/local/sbin:$PATH"

#   Java
    export JAVA_HOME=/Library/Java/JavaVirtualMachines/jdk1.7.0_60.jdk/Contents/Home

# Python
    # pip should only run if there is a virtualenv currently activated
    # export PIP_REQUIRE_VIRTUALENV=true
    # cache pip-installed packages to avoid re-downloading
    # export PIP_DOWNLOAD_CACHE=$HOME/.pip/cache


#   -----------------------------
#   2.  MAKE TERMINAL BETTER
#   -----------------------------

    alias cp='cp -iv'                           # Preferred 'cp' implementation
    alias mv='mv -iv'                           # Preferred 'mv' implementation
    # Create intermediate directories as required
    alias mkdir='mkdir -pv'                     # Preferred 'mkdir' implementation
    # list the files with color (G), no group id (o), include . started entries,
    # display '/' for directory, symbolic links on the command line are followed (H)
    #alias ll='ls -GoHFa'
    alias ll='ls -FGlAhp'                       # Preferred 'ls' implementation
    alias less='less -FSRXc'                    # Preferred 'less' implementation
    cd() { builtin cd "$@"; ll; }               # Always list directory contents upon 'cd'
    alias cd..='cd ../'                         # Go back 1 directory level (for fast typers)
    alias ..='cd ../'                           # Go back 1 directory level
    alias ...='cd ../../'                       # Go back 2 directory levels
    alias .3='cd ../../../'                     # Go back 3 directory levels
    alias .4='cd ../../../../'                  # Go back 4 directory levels
    alias .5='cd ../../../../../'               # Go back 5 directory levels
    alias .6='cd ../../../../../../'            # Go back 6 directory levels
    alias edit='subl'                           # edit:         Opens any file in sublime editor
    alias f='open -a Finder ./'                 # f:            Opens current directory in MacOS Finder
    alias ~="cd ~"                              # ~:            Go Home
    alias c='clear'                             # c:            Clear terminal display
    alias which='type -all'                     # which:        Find executables
    alias path='echo -e ${PATH//:/\\n}'         # path:         Echo all executable Paths
    alias show_options='shopt'                  # Show_options: display bash options settings
    alias fix_stty='stty sane'                  # fix_stty:     Restore terminal settings when screwed up
    alias cic='set completion-ignore-case On'   # cic:          Make tab-completion case-insensitive
    mcd () { mkdir -p "$1" && cd "$1"; }        # mcd:          Makes new Dir and jumps inside
    trash () { command mv "$@" ~/.Trash ; }     # trash:        Moves a file to the MacOS trash
    ql () { qlmanage -p "$*" >& /dev/null; }    # ql:           Opens any file in MacOS Quicklook Preview
    alias DT='tee ~/Desktop/terminalOut.txt'    # DT:           Pipe content to file on MacOS Desktop

    #   lr:  Full Recursive Directory Listing
    alias lr='ls -R | grep ":$" | sed -e '\''s/:$//'\'' -e '\''s/[^-][^\/]*\//--/g'\'' -e '\''s/^/   /'\'' -e '\''s/-/|/'\'' | less'

    #  Update the name of the terminal tab
    function tabname {
      printf "\e]1;$1\a"
    }

    #  Update the name of the terminal window
    function winname {
      printf "\e]2;$1\a"
    }

    if [ -f ~/.git-completion.bash ]; then
      . ~/.git-completion.bash
    fi


#   -------------------------------
#   3.  FILE AND FOLDER MANAGEMENT
#   -------------------------------


#   ---------------------------
#   4.  SEARCHING
#   ---------------------------

    alias qfind="find . -name "                 # qfind:    Quickly search for file
    ff () { /usr/bin/find . -name "$@" ; }      # ff:       Find file under the current directory
    ffs () { /usr/bin/find . -name "$@"'*' ; }  # ffs:      Find file whose name starts with a given string
    ffe () { /usr/bin/find . -name '*'"$@" ; }  # ffe:      Find file whose name ends with a given string


