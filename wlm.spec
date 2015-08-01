Name:		wlm
Version:	1.7
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
Requires:   python3-pygal
Requires:   python3-alembic
Requires:   python3-requests
Requires:   python3-flask-login
Requires:	httpd
Requires:	python3-mod_wsgi
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

cp -a wlm alembic* application manage.py %{buildroot}%{_datadir}/wlm/
cp -a config/* %{buildroot}%{_sysconfdir}/wlm/
cp -a httpd.wlm.conf %{buildroot}%{_sysconfdir}/httpd/conf.d/01_wlm.conf

%pre
getent group wlm >/dev/null || groupadd -r wlm
getent passwd wlm >/dev/null || \
useradd -r -g wlm -G wlm -d %{_datadir}/wlm/wlm -s /bin/bash -c "WLM user" wlm
/usr/bin/passwd -l wlm >/dev/null

%post
service httpd condrestart

%files
%dir %{_sysconfdir}/wlm
#%dir %{_sharedstatedir}/wlm
%{_datadir}/wlm
%config(noreplace) %{_sysconfdir}/httpd/conf.d/01_wlm.conf

#%defattr(-, wlm, wlm, -)
#%dir %{_sharedstatedir}/wlm/data

%defattr(600, wlm, wlm, 700)
%config(noreplace) %{_sysconfdir}/wlm/wlm.conf

%changelog
* Sat Aug 01 2015 Miroslav Suchý <miroslav@suchy.cz> 1.7-1
- add image gallery
- make index page nicer
- add some content
- clarify comment
- rename wlm.conf to 01_wlm.conf
- use ssl
- fix typo
- fix login process
- add upgrade sql script
- add login
- request python3-requests
- implement google+ login
- do not include /usr/share/wlm twice
- update /render/day/
- create /render/day/
- second iteration of year-month render
- first version of /render/year-month/
- fix releaser url

* Sun Nov 23 2014 Miroslav Suchý <miroslav@suchy.cz> 1.6-1
- fix syntax error

* Sun Nov 23 2014 Miroslav Suchý <miroslav@suchy.cz> 1.5-1
- add login template
- if mac addr is not registred return 404
- for some reason xrange does not work here

* Sat Sep 20 2014 Miroslav Suchý <miroslav@suchy.cz> 1.4-1
- save data in db
- create new Measurement  instance
- parse data from sensor
- use python3-mod_wsgi
- allow httpd to start
- add notest to setup.txt
- configure alembic to not use separate password
- add pygal to requires
- do not put email in changelog

* Thu Aug 28 2014 Miroslav Suchý <miroslav@suchy.cz> 1.3-1
- include manage.py in pkg
- configure copr releaser

* Thu Aug 28 2014 Miroslav Suchý <miroslav@suchy.cz> 1.2-1
- add Cop releaser
- package is noarch
- add alembic to rpm
- data dir is not used now
- fix name of variable

* Tue Aug 26 2014 Miroslav Suchý 1.1-1
- new package built with tito


