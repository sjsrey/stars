# Using Vagrant for stars development


## Windows

- install vagrant
- install gitbash
- install cygwin 


### X11 Fowrading

From windows start menu run XWin Server

start gitbash

in gitbash use `export DISPLAY=localhost:0.0` in a session or add it to your
`$HOME/.bashrc` file

connect to vagrant in gitbash:

	vagrant -Y ssh

Forwarding should work from here
