%define bdbv 4.8.30
%global selinux_variants mls strict targeted

%if 0%{?_no_gui:1}
%define _buildqt 0
%define buildargs --with-gui=no
%else
%define _buildqt 1
%if 0%{?_use_qt4}
%define buildargs --with-qrencode --with-gui=qt4
%else
%define buildargs --with-qrencode --with-gui=qt5
%endif
%endif

Name:		GameBit
Version:	0.12.0
Release:	2%{?dist}
Summary:	Peer to Peer Cryptographic Currency

Group:		Applications/System
License:	MIT
URL:		https://GameBit.org/
Source0:	https://GameBit.org/bin/GameBit-core-%{version}/GameBit-%{version}.tar.gz
Source1:	http://download.oracle.com/berkeley-db/db-%{bdbv}.NC.tar.gz

Source10:	https://raw.githubusercontent.com/GameBit/GameBit/v%{version}/contrib/debian/examples/GameBit.conf

#man pages
Source20:	https://raw.githubusercontent.com/GameBit/GameBit/v%{version}/contrib/debian/manpages/GameBitd.1
Source21:	https://raw.githubusercontent.com/GameBit/GameBit/v%{version}/contrib/debian/manpages/GameBit-cli.1
Source22:	https://raw.githubusercontent.com/GameBit/GameBit/v%{version}/contrib/debian/manpages/GameBit-qt.1
Source23:	https://raw.githubusercontent.com/GameBit/GameBit/v%{version}/contrib/debian/manpages/GameBit.conf.5

#selinux
Source30:	https://raw.githubusercontent.com/GameBit/GameBit/v%{version}/contrib/rpm/GameBit.te
# Source31 - what about GameBit-tx and bench_GameBit ???
Source31:	https://raw.githubusercontent.com/GameBit/GameBit/v%{version}/contrib/rpm/GameBit.fc
Source32:	https://raw.githubusercontent.com/GameBit/GameBit/v%{version}/contrib/rpm/GameBit.if

Source100:	https://upload.wikimedia.org/wikipedia/commons/4/46/GameBit.svg

%if 0%{?_use_libressl:1}
BuildRequires:	libressl-devel
%else
BuildRequires:	openssl-devel
%endif
BuildRequires:	boost-devel
BuildRequires:	miniupnpc-devel
BuildRequires:	autoconf automake libtool
BuildRequires:	libevent-devel


Patch0:		GameBit-0.12.0-libressl.patch


%description
GameBit is a digital cryptographic currency that uses peer-to-peer technology to
operate with no central authority or banks; managing transactions and the
issuing of GameBits is carried out collectively by the network.

%if %{_buildqt}
%package core
Summary:	Peer to Peer Cryptographic Currency
Group:		Applications/System
Obsoletes:	%{name} < %{version}-%{release}
Provides:	%{name} = %{version}-%{release}
%if 0%{?_use_qt4}
BuildRequires:	qt-devel
%else
BuildRequires:	qt5-qtbase-devel
# for /usr/bin/lrelease-qt5
BuildRequires:	qt5-linguist
%endif
BuildRequires:	protobuf-devel
BuildRequires:	qrencode-devel
BuildRequires:	%{_bindir}/desktop-file-validate
# for icon generation from SVG
BuildRequires:	%{_bindir}/inkscape
BuildRequires:	%{_bindir}/convert

%description core
GameBit is a digital cryptographic currency that uses peer-to-peer technology to
operate with no central authority or banks; managing transactions and the
issuing of GameBits is carried out collectively by the network.

This package contains the Qt based graphical client and node. If you are looking
to run a GameBit wallet, this is probably the package you want.
%endif


%package libs
Summary:	GameBit shared libraries
Group:		System Environment/Libraries

%description libs
This package provides the GameBitconsensus shared libraries. These libraries
may be used by third party software to provide consensus verification
functionality.

Unless you know need this package, you probably do not.

%package devel
Summary:	Development files for GameBit
Group:		Development/Libraries
Requires:	%{name}-libs = %{version}-%{release}

%description devel
This package contains the header files and static library for the
GameBitconsensus shared library. If you are developing or compiling software
that wants to link against that library, then you need this package installed.

Most people do not need this package installed.

%package server
Summary:	The GameBit daemon
Group:		System Environment/Daemons
Requires:	GameBit-utils = %{version}-%{release}
Requires:	selinux-policy policycoreutils-python
Requires(pre):	shadow-utils
Requires(post):	%{_sbindir}/semodule %{_sbindir}/restorecon %{_sbindir}/fixfiles %{_sbindir}/sestatus
Requires(postun):	%{_sbindir}/semodule %{_sbindir}/restorecon %{_sbindir}/fixfiles %{_sbindir}/sestatus
BuildRequires:	systemd
BuildRequires:	checkpolicy
BuildRequires:	%{_datadir}/selinux/devel/Makefile

%description server
This package provides a stand-alone GameBit-core daemon. For most users, this
package is only needed if they need a full-node without the graphical client.

Some third party wallet software will want this package to provide the actual
GameBit-core node they use to connect to the network.

If you use the graphical GameBit-core client then you almost certainly do not
need this package.

%package utils
Summary:	GameBit utilities
Group:		Applications/System

%description utils
This package provides several command line utilities for interacting with a
GameBit-core daemon.

The GameBit-cli utility allows you to communicate and control a GameBit daemon
over RPC, the GameBit-tx utility allows you to create a custom transaction, and
the bench_GameBit utility can be used to perform some benchmarks.

This package contains utilities needed by the GameBit-server package.


%prep
%setup -q
%patch0 -p1 -b .libressl
cp -p %{SOURCE10} ./GameBit.conf.example
tar -zxf %{SOURCE1}
cp -p db-%{bdbv}.NC/LICENSE ./db-%{bdbv}.NC-LICENSE
mkdir db4 SELinux
cp -p %{SOURCE30} %{SOURCE31} %{SOURCE32} SELinux/


%build
CWD=`pwd`
cd db-%{bdbv}.NC/build_unix/
../dist/configure --enable-cxx --disable-shared --with-pic --prefix=${CWD}/db4
make install
cd ../..

./autogen.sh
%configure LDFLAGS="-L${CWD}/db4/lib/" CPPFLAGS="-I${CWD}/db4/include/" --with-miniupnpc --enable-glibc-back-compat %{buildargs}
make %{?_smp_mflags}

pushd SELinux
for selinuxvariant in %{selinux_variants}; do
	make NAME=${selinuxvariant} -f %{_datadir}/selinux/devel/Makefile
	mv GameBit.pp GameBit.pp.${selinuxvariant}
	make NAME=${selinuxvariant} -f %{_datadir}/selinux/devel/Makefile clean
done
popd


%install
make install DESTDIR=%{buildroot}

mkdir -p -m755 %{buildroot}%{_sbindir}
mv %{buildroot}%{_bindir}/GameBitd %{buildroot}%{_sbindir}/GameBitd

# systemd stuff
mkdir -p %{buildroot}%{_tmpfilesdir}
cat <<EOF > %{buildroot}%{_tmpfilesdir}/GameBit.conf
d /run/GameBitd 0750 GameBit GameBit -
EOF
touch -a -m -t 201504280000 %{buildroot}%{_tmpfilesdir}/GameBit.conf

mkdir -p %{buildroot}%{_sysconfdir}/sysconfig
cat <<EOF > %{buildroot}%{_sysconfdir}/sysconfig/GameBit
# Provide options to the GameBit daemon here, for example
# OPTIONS="-testnet -disable-wallet"

OPTIONS=""

# System service defaults.
# Don't change these unless you know what you're doing.
CONFIG_FILE="%{_sysconfdir}/GameBit/GameBit.conf"
DATA_DIR="%{_localstatedir}/lib/GameBit"
PID_FILE="/run/GameBitd/GameBitd.pid"
EOF
touch -a -m -t 201504280000 %{buildroot}%{_sysconfdir}/sysconfig/GameBit

mkdir -p %{buildroot}%{_unitdir}
cat <<EOF > %{buildroot}%{_unitdir}/GameBit.service
[Unit]
Description=GameBit daemon
After=syslog.target network.target

[Service]
Type=forking
ExecStart=%{_sbindir}/GameBitd -daemon -conf=\${CONFIG_FILE} -datadir=\${DATA_DIR} -pid=\${PID_FILE} \$OPTIONS
EnvironmentFile=%{_sysconfdir}/sysconfig/GameBit
User=GameBit
Group=GameBit

Restart=on-failure
PrivateTmp=true
TimeoutStopSec=120
TimeoutStartSec=60
StartLimitInterval=240
StartLimitBurst=5

[Install]
WantedBy=multi-user.target
EOF
touch -a -m -t 201504280000 %{buildroot}%{_unitdir}/GameBit.service
#end systemd stuff

mkdir %{buildroot}%{_sysconfdir}/GameBit
mkdir -p %{buildroot}%{_localstatedir}/lib/GameBit

#SELinux
for selinuxvariant in %{selinux_variants}; do
	install -d %{buildroot}%{_datadir}/selinux/${selinuxvariant}
	install -p -m 644 SELinux/GameBit.pp.${selinuxvariant} %{buildroot}%{_datadir}/selinux/${selinuxvariant}/GameBit.pp
done

%if %{_buildqt}
# qt icons
install -D -p share/pixmaps/GameBit.ico %{buildroot}%{_datadir}/pixmaps/GameBit.ico
install -p share/pixmaps/nsis-header.bmp %{buildroot}%{_datadir}/pixmaps/
install -p share/pixmaps/nsis-wizard.bmp %{buildroot}%{_datadir}/pixmaps/
install -p %{SOURCE100} %{buildroot}%{_datadir}/pixmaps/GameBit.svg
%{_bindir}/inkscape %{SOURCE100} --export-png=%{buildroot}%{_datadir}/pixmaps/GameBit16.png -w16 -h16
%{_bindir}/inkscape %{SOURCE100} --export-png=%{buildroot}%{_datadir}/pixmaps/GameBit32.png -w32 -h32
%{_bindir}/inkscape %{SOURCE100} --export-png=%{buildroot}%{_datadir}/pixmaps/GameBit64.png -w64 -h64
%{_bindir}/inkscape %{SOURCE100} --export-png=%{buildroot}%{_datadir}/pixmaps/GameBit128.png -w128 -h128
%{_bindir}/inkscape %{SOURCE100} --export-png=%{buildroot}%{_datadir}/pixmaps/GameBit256.png -w256 -h256
%{_bindir}/convert -resize 16x16 %{buildroot}%{_datadir}/pixmaps/GameBit256.png %{buildroot}%{_datadir}/pixmaps/GameBit16.xpm
%{_bindir}/convert -resize 32x32 %{buildroot}%{_datadir}/pixmaps/GameBit256.png %{buildroot}%{_datadir}/pixmaps/GameBit32.xpm
%{_bindir}/convert -resize 64x64 %{buildroot}%{_datadir}/pixmaps/GameBit256.png %{buildroot}%{_datadir}/pixmaps/GameBit64.xpm
%{_bindir}/convert -resize 128x128 %{buildroot}%{_datadir}/pixmaps/GameBit256.png %{buildroot}%{_datadir}/pixmaps/GameBit128.xpm
%{_bindir}/convert %{buildroot}%{_datadir}/pixmaps/GameBit256.png %{buildroot}%{_datadir}/pixmaps/GameBit256.xpm
touch %{buildroot}%{_datadir}/pixmaps/*.png -r %{SOURCE100}
touch %{buildroot}%{_datadir}/pixmaps/*.xpm -r %{SOURCE100}

# Desktop File - change the touch timestamp if modifying
mkdir -p %{buildroot}%{_datadir}/applications
cat <<EOF > %{buildroot}%{_datadir}/applications/GameBit-core.desktop
[Desktop Entry]
Encoding=UTF-8
Name=GameBit
Comment=GameBit P2P Cryptocurrency
Comment[fr]=GameBit, monnaie virtuelle cryptographique pair à pair
Comment[tr]=GameBit, eşten eşe kriptografik sanal para birimi
Exec=GameBit-qt %u
Terminal=false
Type=Application
Icon=GameBit128
MimeType=x-scheme-handler/GameBit;
Categories=Office;Finance;
EOF
# change touch date when modifying desktop
touch -a -m -t 201511100546 %{buildroot}%{_datadir}/applications/GameBit-core.desktop
%{_bindir}/desktop-file-validate %{buildroot}%{_datadir}/applications/GameBit-core.desktop

# KDE protocol - change the touch timestamp if modifying
mkdir -p %{buildroot}%{_datadir}/kde4/services
cat <<EOF > %{buildroot}%{_datadir}/kde4/services/GameBit-core.protocol
[Protocol]
exec=GameBit-qt '%u'
protocol=GameBit
input=none
output=none
helper=true
listing=
reading=false
writing=false
makedir=false
deleting=false
EOF
# change touch date when modifying protocol
touch -a -m -t 201511100546 %{buildroot}%{_datadir}/kde4/services/GameBit-core.protocol
%endif

# man pages
install -D -p %{SOURCE20} %{buildroot}%{_mandir}/man1/GameBitd.1
install -p %{SOURCE21} %{buildroot}%{_mandir}/man1/GameBit-cli.1
%if %{_buildqt}
install -p %{SOURCE22} %{buildroot}%{_mandir}/man1/GameBit-qt.1
%endif
install -D -p %{SOURCE23} %{buildroot}%{_mandir}/man5/GameBit.conf.5

# nuke these, we do extensive testing of binaries in %%check before packaging
rm -f %{buildroot}%{_bindir}/test_*

%check
make check
pushd src
srcdir=. test/GameBit-util-test.py
popd
qa/pull-tester/rpc-tests.py -extended

%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig

%pre server
getent group GameBit >/dev/null || groupadd -r GameBit
getent passwd GameBit >/dev/null ||
	useradd -r -g GameBit -d /var/lib/GameBit -s /sbin/nologin \
	-c "GameBit wallet server" GameBit
exit 0

%post server
%systemd_post GameBit.service
# SELinux
if [ `%{_sbindir}/sestatus |grep -c "disabled"` -eq 0 ]; then
for selinuxvariant in %{selinux_variants}; do
	%{_sbindir}/semodule -s ${selinuxvariant} -i %{_datadir}/selinux/${selinuxvariant}/GameBit.pp &> /dev/null || :
done
%{_sbindir}/semanage port -a -t GameBit_port_t -p tcp 8370
%{_sbindir}/semanage port -a -t GameBit_port_t -p tcp 8369
%{_sbindir}/semanage port -a -t GameBit_port_t -p tcp 18370
%{_sbindir}/semanage port -a -t GameBit_port_t -p tcp 18369
%{_sbindir}/fixfiles -R GameBit-server restore &> /dev/null || :
%{_sbindir}/restorecon -R %{_localstatedir}/lib/GameBit || :
fi

%posttrans server
%{_bindir}/systemd-tmpfiles --create

%preun server
%systemd_preun GameBit.service

%postun server
%systemd_postun GameBit.service
# SELinux
if [ $1 -eq 0 ]; then
	if [ `%{_sbindir}/sestatus |grep -c "disabled"` -eq 0 ]; then
	%{_sbindir}/semanage port -d -p tcp 8370
	%{_sbindir}/semanage port -d -p tcp 8369
	%{_sbindir}/semanage port -d -p tcp 18370
	%{_sbindir}/semanage port -d -p tcp 18369
	for selinuxvariant in %{selinux_variants}; do
		%{_sbindir}/semodule -s ${selinuxvariant} -r GameBit &> /dev/null || :
	done
	%{_sbindir}/fixfiles -R GameBit-server restore &> /dev/null || :
	[ -d %{_localstatedir}/lib/GameBit ] && \
		%{_sbindir}/restorecon -R %{_localstatedir}/lib/GameBit &> /dev/null || :
	fi
fi

%clean
rm -rf %{buildroot}

%if %{_buildqt}
%files core
%defattr(-,root,root,-)
%license COPYING db-%{bdbv}.NC-LICENSE
%doc COPYING GameBit.conf.example doc/README.md doc/bips.md doc/files.md doc/multiwallet-qt.md doc/reduce-traffic.md doc/release-notes.md doc/tor.md
%attr(0755,root,root) %{_bindir}/GameBit-qt
%attr(0644,root,root) %{_datadir}/applications/GameBit-core.desktop
%attr(0644,root,root) %{_datadir}/kde4/services/GameBit-core.protocol
%attr(0644,root,root) %{_datadir}/pixmaps/*.ico
%attr(0644,root,root) %{_datadir}/pixmaps/*.bmp
%attr(0644,root,root) %{_datadir}/pixmaps/*.svg
%attr(0644,root,root) %{_datadir}/pixmaps/*.png
%attr(0644,root,root) %{_datadir}/pixmaps/*.xpm
%attr(0644,root,root) %{_mandir}/man1/GameBit-qt.1*
%endif

%files libs
%defattr(-,root,root,-)
%license COPYING
%doc COPYING doc/README.md doc/shared-libraries.md
%{_libdir}/lib*.so.*

%files devel
%defattr(-,root,root,-)
%license COPYING
%doc COPYING doc/README.md doc/developer-notes.md doc/shared-libraries.md
%attr(0644,root,root) %{_includedir}/*.h
%{_libdir}/*.so
%{_libdir}/*.a
%{_libdir}/*.la
%attr(0644,root,root) %{_libdir}/pkgconfig/*.pc

%files server
%defattr(-,root,root,-)
%license COPYING db-%{bdbv}.NC-LICENSE
%doc COPYING GameBit.conf.example doc/README.md doc/REST-interface.md doc/bips.md doc/dnsseed-policy.md doc/files.md doc/reduce-traffic.md doc/release-notes.md doc/tor.md
%attr(0755,root,root) %{_sbindir}/GameBitd
%attr(0644,root,root) %{_tmpfilesdir}/GameBit.conf
%attr(0644,root,root) %{_unitdir}/GameBit.service
%dir %attr(0750,GameBit,GameBit) %{_sysconfdir}/GameBit
%dir %attr(0750,GameBit,GameBit) %{_localstatedir}/lib/GameBit
%config(noreplace) %attr(0600,root,root) %{_sysconfdir}/sysconfig/GameBit
%attr(0644,root,root) %{_datadir}/selinux/*/*.pp
%attr(0644,root,root) %{_mandir}/man1/GameBitd.1*
%attr(0644,root,root) %{_mandir}/man5/GameBit.conf.5*

%files utils
%defattr(-,root,root,-)
%license COPYING
%doc COPYING GameBit.conf.example doc/README.md
%attr(0755,root,root) %{_bindir}/GameBit-cli
%attr(0755,root,root) %{_bindir}/GameBit-tx
%attr(0755,root,root) %{_bindir}/bench_GameBit
%attr(0644,root,root) %{_mandir}/man1/GameBit-cli.1*
%attr(0644,root,root) %{_mandir}/man5/GameBit.conf.5*



%changelog
* Fri Feb 26 2016 Alice Wonder <buildmaster@librelamp.com> - 0.12.0-2
- Rename Qt package from GameBit to GameBit-core
- Make building of the Qt package optional
- When building the Qt package, default to Qt5 but allow building
-  against Qt4
- Only run SELinux stuff in post scripts if it is not set to disabled

* Wed Feb 24 2016 Alice Wonder <buildmaster@librelamp.com> - 0.12.0-1
- Initial spec file for 0.12.0 release

# This spec file is written from scratch but a lot of the packaging decisions are directly
# based upon the 0.11.2 package spec file from https://www.ringingliberty.com/GameBit/
