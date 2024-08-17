Name: cloudberry-dev-repo
Version: 1.0
Release: 1%{?dist}
Summary: Cloudberry Dev Repository Configuration
License: Apache-2.0
Group: Development/Tools

%description
This package configures the Cloudberry Dev repository on your system.

%install
mkdir -p %{buildroot}%{_sysconfdir}/yum.repos.d/
cat > %{buildroot}%{_sysconfdir}/yum.repos.d/cloudberry-dev.repo <<EOF
[cloudberry-dev]
name=Cloudberry Dev Repository
baseurl=https://aws-codeartifact-us-east-1.s3.amazonaws.com/cloudberry-dev/rpm-packages
enabled=1
gpgcheck=0
EOF

cat > %{buildroot}%{_sysconfdir}/apt/sources.list.d/cloudberry-dev.list <<EOF
deb https://aws-codeartifact-us-east-1.s3.amazonaws.com/cloudberry-dev/deb-packages /
EOF

%files
%{_sysconfdir}/yum.repos.d/cloudberry-dev.repo
%{_sysconfdir}/apt/sources.list.d/cloudberry-dev.list

%post
yum clean all
yum makecache
apt-get update

%changelog
* Mon Aug 14 2023 Your Name <your@email.com> 1.0-1
- Initial versionng
