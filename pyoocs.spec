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

%prep
%setup -q

%build
CFLAGS="%{optflags}" %{__python} setup.py build

%install
[ "%{buildroot}" != / ] && rm -rf "%{buildroot}"
%{__python} setup.py install \
   -O1 --skip-build \
   --root="%{buildroot}" \
   --install-headers=%{_includedir}/python \
   --install-lib=%{python_sitearch}

install -d %{buildroot}%{_sysconfdir}
install -m 0644 oocs-cfg.json %{buildroot}%{_sysconfdir}/oocs-cfg.json

%files
%defattr(-,root,root)
%{_bindir}/pyoocs.py
%{_bindir}/pyoocs-htmlviewer.py
%{python_sitearch}/*.egg-info
%{python_sitearch}/*.so
%{python_sitearch}/oocs/*.py*
%config(noreplace) %{_sysconfdir}/oocs-cfg.json
%doc LICENSE README.md

%changelog
* Tue Feb 09 2016 Davide Madrisan <davide.madrisan@gmail.com> 0-1mamba
- package created by autospec
