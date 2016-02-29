%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(plat_specific=1)")}

%global srcname pyoocs
%global modname oocs

Name:           python-%{srcname}
Version:        0
Release:        1%{?dist}
Summary:        Out of Compliance Scanner for Linux

Group:          Applications/System
License:        GPLv3
URL:            https://github.com/madrisan/pyoocs
Source0:        https://github.com/madrisan/pyoocs.git/master/pyoocs-%{version}.tar.bz2
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  glibc-devel
BuildRequires:  python-devel

%description
Out of Compliance Scanner for Linux.                   \
A customizable and modular security scanner for Linux.


%prep
%setup -q -n %{srcname}-%{version}


%build
%{__python} setup.py build


%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT
install -D -m 0644 oocs-cfg.json %{buildroot}%{_sysconfdir}/oocs-cfg.json


%clean
rm -rf $RPM_BUILD_ROOT


%files -n python-%{srcname}
%doc LICENSE
%{_bindir}/pyoocs-htmlviewer.py
%{_bindir}/pyoocs.py
%{python_sitelib}/%{modname}
%{_sysconfdir}/oocs-cfg.json

%changelog
* Wed Feb 10 2016 Davide Madrisan <davide.madrisan@gmail.com> - 0-1
- package created by autospec
