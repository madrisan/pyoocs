%if 0%{?fedora} || 0%{?rhel} >= 8
%global with_py3 1
%endif

%global srcname pyoocs
%global modname oocs

Name:           python-%{srcname}
Version:        0
Release:        1%{?dist}
Summary:        Out of Compliance Scanner for Linux

License:        GPLv3
URL:            https://github.com/madrisan/pyoocs
Source0:        https://github.com/madrisan/pyoocs.git/master/pyoocs-%{version}.tar.bz2

BuildRequires:  glibc-devel
BuildRequires:  python-devel

%if 0%{?with_py3}
BuildRequires:  python3-devel
%endif

%global common_desc                                    \
Out of Compliance Scanner for Linux.                   \
A customizable and modular security scanner for Linux.

%description
%{common_desc}

%package -n python2-%{srcname}
Summary:        Out of Compliance Scanner for Linux

%{?python_provide:%python_provide python2-%{srcname}}

%description -n python2-%{srcname}
%{common_desc}

%if 0%{?with_py3}
%package -n python3-%{srcname}
Summary:        Out of Compliance Scanner for Linux

%{?python_provide:%python_provide python3-%{srcname}}

%description -n python3-%{srcname}
%{common_desc}
%endif

%prep
%setup -q -c

%if 0%{?with_py3}
# Prepare for a python3 build
cp -a %{srcname}-%{version} python3-%{srcname}-%{version}
%endif

%build

# Python 2 build
pushd %{srcname}-%{version}
%py2_build
popd

%if 0%{?with_py3}
# Python 3 build
pushd python3-%{srcname}-%{version}
%py3_build
popd
%endif

%install
# Python 2 install
pushd %{srcname}-%{version}
%py2_install
install -D -m 0644 oocs-cfg.json %{buildroot}%{_sysconfdir}/oocs-cfg.json
popd

%if 0%{?with_py3}
# Python 3 install
pushd python3-%{srcname}-%{version}
%py3_install
install -D -m 0644 oocs-cfg.json %{buildroot}%{_sysconfdir}/oocs-cfg.json
popd
%endif

%files -n python2-%{srcname}
%license %{srcname}-%{version}/LICENSE
%{_bindir}/pyoocs-htmlviewer.py
%{_bindir}/pyoocs.py
%{python2_sitearch}/%{modname}
%{python2_sitearch}/*.egg-info
%{_sysconfdir}/oocs-cfg.json

%if 0%{?with_py3}
%files -n python3-%{srcname}
%license %{srcname}-%{version}/LICENSE
%{_bindir}/pyoocs-htmlviewer.py
%{_bindir}/pyoocs.py
%{python3_sitearch}/%{modname}
%{python3_sitearch}/*.egg-info
%{_sysconfdir}/oocs-cfg.json
%endif

%changelog
* Wed Feb 10 2016 Davide Madrisan <davide.madrisan@gmail.com> - 0-1
- package created by autospec
