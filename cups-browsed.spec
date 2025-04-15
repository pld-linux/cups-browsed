Summary:	A daemon for browsing the Bonjour broadcasts of shared, remote CUPS printers
Summary(pl.UTF-8):	Demon do przeglądania broadcastów Bonjour współdzielonych, zdalnych drukarek CUPS
Name:		cups-browsed
Version:	2.1.1
Release:	1
# For a breakdown of the licensing, see COPYING file
# LGPLv2+:   utils: cups-browsed
License:	GPL v2, GPL v2+, GPL v3, GPL v3+, LGPL v2+, MIT
Group:		Applications/Printing
#Source0:	https://www.openprinting.org/download/cups-filters/%{name}-%{version}.tar.xz
Source0:	https://github.com/OpenPrinting/cups-browsed/releases/download/%{version}/%{name}-%{version}.tar.xz
# Source0-md5:	293948973ebfc7ef4d5d8242d5733181
URL:		http://www.linuxfoundation.org/collaborate/workgroups/openprinting/cups-browsed
BuildRequires:	avahi-devel
BuildRequires:	avahi-glib-devel
BuildRequires:	cups-devel >= 1:1.6.0
BuildRequires:	dbus-devel
BuildRequires:	gettext-tools
BuildRequires:	glib2-devel >= 1:2.30.2
BuildRequires:	libcupsfilters-devel
BuildRequires:	libppd-devel
BuildRequires:	pkgconfig >= 1:0.20
BuildRequires:	rpmbuild(macros) >= 1.671
BuildRequires:	tar >= 1:1.22
BuildRequires:	xz
BuildRequires:	zlib-devel
Requires(post,preun):	/sbin/chkconfig
Requires(post,preun,postun):	systemd-units
Requires:	glib2 >= 1:2.30.2
Requires:	systemd-units >= 38
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_cups_serverbin		%(/usr/bin/cups-config --serverbin)

%description -n cups-browsed
A daemon for browsing the Bonjour broadcasts of shared, remote CUPS
printers.

%description -n cups-browsed -l pl.UTF-8
Demon do przeglądania broadcastów Bonjour współdzielonych, zdalnych
drukarek CUPS.

%prep
%setup -q

%build
%configure \
	--with-rcdir=/etc/rc.d

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{systemdunitdir}
%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install -p daemon/cups-browsed.service $RPM_BUILD_ROOT%{systemdunitdir}

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ "$1" = "1" ]; then
	# We can remove this after few releases, it's just for the introduction of cups-browsed.
	if [ -f %{_sysconfdir}/cups/cups-browsed.conf ]; then
		echo -e "\n# NOTE: This file is not part of CUPS. You need to start & enable cups-browsed service." >>%{_sysconfdir}/cups/cups-browsed.conf
	fi

	# move BrowsePoll from cupsd.conf to cups-browsed.conf
	if [ -f %{_sysconfdir}/cups/cupsd.conf ] && grep -iq "^BrowsePoll" %{_sysconfdir}/cups/cupsd.conf; then
		if ! grep -iq "^BrowsePoll" %{_sysconfdir}/cups/cups-browsed.conf; then
			echo "# Settings automatically moved from cupsd.conf by RPM package:" >>%{_sysconfdir}/cups/cups-browsed.conf
			grep -i "^BrowsePoll" %{_sysconfdir}/cups/cupsd.conf >> %{_sysconfdir}/cups/cups-browsed.conf || :
		fi
		sed -i -e "s,^BrowsePoll,#BrowsePoll directive moved to cups-browsed.conf\n#BrowsePoll,i" %{_sysconfdir}/cups/cupsd.conf || :
	fi
fi
/sbin/chkconfig --add cups-browsed
%service cups-browsed restart
%systemd_post cups-browsed.service

%preun
if [ "$1" = "0" ]; then
	%service cups-browsed stop
	/sbin/chkconfig --del cups-browsed
fi
%systemd_preun cups-browsed.service

%postun
%systemd_reload

%files
%defattr(644,root,root,755)
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/cups/cups-browsed.conf
%attr(755,root,root) %{_sbindir}/cups-browsed
%attr(754,root,root) /etc/rc.d/init.d/cups-browsed
%attr(754,root,root) %{_cups_serverbin}/backend/implicitclass
%{systemdunitdir}/cups-browsed.service
%{_mandir}/man5/cups-browsed.conf.5*
%{_mandir}/man8/cups-browsed.8*
