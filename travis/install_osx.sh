#!/bin/bash
# Script installing dependencies
# Inspired by https://github.com/google/fruit

set -e

# Helper for travis folding
travis_fold() {
  local action=$1
  local name=$2
  echo -en "travis_fold:${action}:${name}\r"
}

# Helper for installing packages via homebrew
install_brew_package() {
  if brew list -1 | grep -q "^$1\$"; then
    # Package is installed, upgrade if needed
    brew outdated "$1" || brew upgrade "$@"
  else
    # Package not installed yet, install.
    brew install "$@" || brew link --overwrite "$@"
  fi
}

# Update packages
travis_fold start brew_update
brew update
travis_fold end brew_update

travis_fold start brew_install_util
# For `timeout'
install_brew_package coreutils

install_brew_package cmake

# Install compiler
case "${COMPILER}" in
gcc)         install_brew_package gcc ;;
gcc-6)       install_brew_package gcc@6 ;;
clang)       ;;
clang-4)     install_brew_package llvm@4 --with-clang --with-libcxx;;
*) echo "Compiler not supported: ${COMPILER}. See travis/install_osx.sh"; exit 1 ;;
esac
travis_fold end brew_install_util


# Install dependencies
travis_fold start brew_install_dependencies
install_brew_package gmp --c++11
install_brew_package cln
install_brew_package ginac
install_brew_package boost --c++11
install_brew_package eigen
install_brew_package python
install_brew_package python3

if [[ "$CONFIG" == *Parser ]]
then
    install_brew_package maven
fi
travis_fold end brew_install_dependencies
