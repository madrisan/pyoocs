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

# git clone https://github.com/madrisan/pyoocs
# mv pyoocs pyoocs-0
# tar -cjf $HOME/rpmbuild/SOURCES/pyoocs-0.tar.bz2 pyoocs-0

Source0:        https://github.com/madrisan/pyoocs.git/master/pyoocs-%{version}.tar.bz2

BuildRequires:  glibc-devel

%if 0%{?with_py3}
BuildRequires:  python3-devel
%else
BuildRequires:  python-devel
%endif

%global common_desc                                    \
Out of Compliance Scanner for Linux.                   \
A customizable and modular security scanner for Linux.

%description
%{common_desc}

%if 0%{?with_py3}
%package -n python3-%{srcname}
Summary:        Out of Compliance Scanner for Linux

%{?python_provide:%python_provide python3-%{srcname}}

%description -n python3-%{srcname}
%{common_desc}

%else

%package -n python2-%{srcname}
Summary:        Out of Compliance Scanner for Linux

%{?python_provide:%python_provide python2-%{srcname}}

%description -n python2-%{srcname}
%{common_desc}
%endif

%prep
%setup -q -n %{srcname}-%{version}

%build
%if 0%{?with_py3}
%py3_build
%else
%py2_build
%endif

%if 0%{?with_py3}
%py3_install
%else
%py2_install
%endif

install -D -m 0644 oocs-cfg.json %{buildroot}%{_sysconfdir}/oocs-cfg.json

%if 0%{?with_py3}
%files -n python3-%{srcname}
%{python3_sitearch}/%{modname}
%{python3_sitearch}/*.egg-info
%else
%files -n python2-%{srcname}
%{python2_sitearch}/%{modname}
%{python2_sitearch}/*.egg-info
%{_sysconfdir}/oocs-cfg.json
%endif
%{_bindir}/pyoocs-htmlviewer.py
%{_bindir}/pyoocs.py
%{_sysconfdir}/oocs-cfg.json
%license LICENSE

%changelog
* Wed Feb 10 2016 Davide Madrisan <davide.madrisan@gmail.com> - 0-1
- package created by autospec
