Name:		wlm
Version:	1.1
Release:	1%{?dist}
Summary:	wlm

Group:		Applications/Communications
License:	GPLv3
URL:		https://github.com/xsuchy/wlm
Source0:	%{name}-%{version}.tar.gz

Requires:	python3-devel
Requires:	python3-flask
Requires:	python3-flask-script
Requires:	python3-flask-sqlalchemy
Requires:	python3-psycopg2
Requires:	httpd
Requires:	mod_wsgi
Requires:	systemd

BuildArch:	noarch
%description
TBD

%prep
%setup -q


%build


%install
install -d %{buildroot}%{_sysconfdir}/wlm
install -d %{buildroot}%{_sysconfdir}/httpd/conf.d
install -d %{buildroot}%{_pkgdocdir}
install -d %{buildroot}%{_datadir}/wlm/

cp -a wlm alembic* application %{buildroot}%{_datadir}/wlm/
cp -a config/* %{buildroot}%{_sysconfdir}/wlm/
cp -a httpd.wlm.conf %{buildroot}%{_sysconfdir}/httpd/conf.d/wlm.conf

%pre
getent group wlm >/dev/null || groupadd -r wlm
getent passwd wlm >/dev/null || \
useradd -r -g wlm -G wlm -d %{_datadir}/wlm/wlm -s /bin/bash -c "WLM user" wlm
/usr/bin/passwd -l wlm >/dev/null

%post
service httpd condrestart

%files
%dir %{_datadir}/wlm
%dir %{_sysconfdir}/wlm
#%dir %{_sharedstatedir}/wlm
%{_datadir}/wlm
%config(noreplace) %{_sysconfdir}/httpd/conf.d/wlm.conf

#%defattr(-, wlm, wlm, -)
#%dir %{_sharedstatedir}/wlm/data

%defattr(600, wlm, wlm, 700)
%config(noreplace) %{_sysconfdir}/wlm/wlm.conf

%changelog
* Tue Aug 26 2014 Miroslav Suchý 1.1-1
- new package built with tito


