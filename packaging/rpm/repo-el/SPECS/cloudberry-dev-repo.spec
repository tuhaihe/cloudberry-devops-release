Name:           cloudberry-dev-repo
Version:        1.0
Release:        1%{?dist}
Summary:        Cloudberry Database Repository Configuration
License:        Apache-2.0
Group:          Development/Tools
URL:            https://github.com/cloudberrydb/cloudberrydb

%description This package configures the Cloudberry Database
repository on your system. Cloudberry Database is an open-source
project aimed at providing a scalable, high-performance SQL database
for analytics. This repository provides access to the latest RPM
packages for Cloudberry Database, allowing you to easily install and
stay up-to-date with the latest developments.

%install
mkdir -p %{buildroot}%{_sysconfdir}/yum.repos.d/
%if 0%{?rhel} == 8
cat > %{buildroot}%{_sysconfdir}/yum.repos.d/cloudberry-dev.repo <<EOF
[cloudberry-dev]
name=Cloudberry Database Repository
baseurl=https://cloudberry-rpm-dev-bucket.s3.amazonaws.com/repo/el8/x86_64/
enabled=1
gpgcheck=1
gpgkey=https://cloudberry-rpm-dev-bucket.s3.amazonaws.com/repo/el8/x86_64/RPM-GPG-KEY-cloudberry
EOF
%endif

%if 0%{?rhel} == 9
cat > %{buildroot}%{_sysconfdir}/yum.repos.d/cloudberry-dev.repo <<EOF
[cloudberry-dev]
name=Cloudberry Database Repository
baseurl=https://cloudberry-rpm-dev-bucket.s3.amazonaws.com/repo/el9/x86_64/
enabled=1
gpgcheck=1
gpgkey=https://cloudberry-rpm-dev-bucket.s3.amazonaws.com/repo/el9/x86_64/RPM-GPG-KEY-cloudberry
EOF
%endif

%files
%{_sysconfdir}/yum.repos.d/cloudberry-dev.repo

%changelog
* Thu Aug 20 2024 Ed Espino  eespino@gmail.com - 1.6.0-15.4-1
- Initial package with binary files under Apache 2.0 License
