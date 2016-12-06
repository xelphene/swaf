# swaf

Steve's Web Application Framework. A simple, functional, extensible web
programming framework.

# Quick Start / Examples

Ubuntu system setup:

```
sudo apt-get install libapache2-mod-wsgi
ln -s /etc/apache2/mods-available/wsgi-* /etc/apache2/mods-enabled/
/etc/init.d/apache
systemctl restart apache2
```

See examples/apache.conf for an example vhost configuration.

See examples/helloworld.py for a trivial demonstration web app.

# Copyright and License

Copyright (C) 2016 Steve Benson

swaf is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free
Software Foundation; either version 3, or (at your option) any later
version.

swaf is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
details.

You should have received a copy of the GNU General Public License along with
this program; see the file LICENSE.  If not, see <http://www.gnu.org/licenses/>.
