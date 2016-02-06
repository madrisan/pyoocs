# rpm build instructions:
#  - python2:  rpmbuild -ba pyoocs.spec
#  - python3:  rpmbuild -ba pyoocs.spec --define="with_pyver 3"

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
BuildRoot:     %{_tmppath}/%{name}-%{version}-root
## AUTOBUILDREQ-BEGIN
BuildRequires: glibc-devel
## AUTOBUILDREQ-END
BuildRequires: libpython-devel
Requires:      python >= %python_version
BuildRoot:     %{_tmppath}/%{name}-%{version}-root

%description
%{summary}.

%if "%{?with_pyver}"
%pyver_package
%endif

%prep
%setup -q

%build
CFLAGS="%{optflags}" %{__python} setup.py build

%install
[ "%{buildroot}" != / ] && rm -rf "%{buildroot}"
%{__python} setup.py install \
   -O1 --skip-build \
   --root="%{buildroot}" \
   --install-headers=%{python_inc} \
   --install-lib=%{python_sitearch}

install -d %{buildroot}%{_sysconfdir}
install -m 0644 oocs-cfg.json %{buildroot}%{_sysconfdir}/oocs-cfg.json

mv %{buildroot}%{_bindir}/pyoocs.py \
   %{buildroot}%{_bindir}/py%{with_pyver}oocs.py
mv %{buildroot}%{_bindir}/pyoocs-htmlviewer.py \
   %{buildroot}%{_bindir}/py%{with_pyver}oocs-htmlviewer.py

%files %{?pyappend}
%defattr(-,root,root)
%{_bindir}/py%{with_pyver}oocs.py
%{_bindir}/py%{with_pyver}oocs-htmlviewer.py
%{python_sitearch}/*.egg-info
%{python_sitearch}/oocs
%config(noreplace) %{_sysconfdir}/oocs-cfg.json
%doc LICENSE README.md

%changelog
* Wed Feb 10 2016 Davide Madrisan <davide.madrisan@gmail.com> 0-1mamba
- package created by autospec
