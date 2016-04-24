# rpm build instructions:
#  - python2:  rpmbuild -ba pyoocs.spec
#  - python3:  rpmbuild -ba pyoocs.spec --define="with_pyver 3"

%global _webserverdir /srv/www-oocs/html/server/public
%global _htmlviewerdir /srv/www-oocs/html/viewer

Name:          pyoocs
Version:       0
Release:       1mamba
Summary:       Out of Compliance Scanner for Linux
Group:         System/Libraries
Vendor:        openmamba
Distribution:  openmamba
Packager:      Davide Madrisan <davide.madrisan@gmail.com>
URL:           https://github.com/madrisan/pyoocs
## GITSOURCE https://github.com/madrisan/pyoocs.git
Source:        https://github.com/madrisan/pyoocs.git/master/pyoocs-%{version}.tar.bz2
License:       GPLv3
Requires:      python >= %python_version
## AUTOBUILDREQ-BEGIN
BuildRequires: glibc-devel
BuildRequires: nodejs
## AUTOBUILDREQ-END
BuildRoot:     %{_tmppath}/%{name}-%{version}-root

%description
%{summary}.

%if 0%{?with_pyver}
%pyver_package
%endif

%package html
Group:         Applications/Security
Summary:       Web Front-end for %{name}

%prep
%setup -q

%build
CFLAGS="%{optflags}" %{__python} setup.py build

# build the front-end AngularJS application
cd html
bower install
npm install
gulp

cd viewer
npm install

%install
[ "%{buildroot}" != / ] && rm -rf "%{buildroot}"
%{__python} setup.py install \
   -O1 --skip-build \
   --root="%{buildroot}" \
   --install-headers=%{python_inc} \
   --install-lib=%{python_sitearch}

install -d %{buildroot}%{_sysconfdir}
install -m 0644 oocs-cfg.json %{buildroot}%{_sysconfdir}/oocs-cfg.json

%if 0%{?with_pyver}
mv %{buildroot}%{_bindir}/pyoocs.py \
   %{buildroot}%{_bindir}/py%{with_pyver}oocs.py
mv %{buildroot}%{_bindir}/pyoocs-htmlviewer.py \
   %{buildroot}%{_bindir}/py%{with_pyver}oocs-htmlviewer.py
%endif

# install the front-end
install -d %{buildroot}%{_webserverdir}
cp -r html/server/public/* %{buildroot}%{_webserverdir}

# install the htmlviewer
install -d %{buildroot}%{_htmlviewerdir}
cp -r html/viewer/* %{buildroot}%{_htmlviewerdir}

%files %{?pyappend}
%defattr(-,root,root)
%{_bindir}/py%{?with_pyver}oocs.py
%{_bindir}/py%{?with_pyver}oocs-htmlviewer.py
%{python_sitearch}/*.egg-info
%{python_sitearch}/oocs
%config(noreplace) %{_sysconfdir}/oocs-cfg.json
%doc LICENSE README.md

%files html
%defattr(-,root,root)
%{_webserverdir}
%{_htmlviewerdir}

%changelog
* Wed Feb 10 2016 Davide Madrisan <davide.madrisan@gmail.com> 0-1mamba
- package created by autospec
