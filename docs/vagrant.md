# Using Vagrant for stars development


## Windows

- install vagrant
- install gitbash
- install cygwin 
	- xorg-server
	- xinit
	- xorg-docs
	- openssh
	See [here](http://stackoverflow.com/questions/20094118/ssh-into-vagrant-with-x-server-set-up) for specific instructions


### X11 Fowrading

From windows start menu run XWin Server

start gitbash

in gitbash use `export DISPLAY=localhost:0.0` in a session or add it to your
`$HOME/.bashrc` file

connect to vagrant in gitbash:

	vagrant -Y ssh

Forwarding should work from here
