Name:           cloudberry-db
Version:        1.5.4
Release:        1%{?dist}
Summary:        High-performance, open-source data warehouse based on PostgreSQL and Greenplum

License:        ASL 2.0
URL:            https://cloudberrydb.org
Source0:        cbdb-binary.tar.gz

# Disable debugsource files
%define _debugsource_template %{nil}

# List runtime dependencies
Requires:       /bin/sh
Requires:       apr
Requires:       audit-libs
Requires:       bzip2-libs
Requires:       cyrus-sasl-lib
Requires:       glibc
Requires:       iproute
Requires:       iputils
Requires:       keyutils-libs
Requires:       krb5-libs
Requires:       libbrotli
Requires:       libcap-ng
Requires:       libcom_err
Requires:       libcurl
Requires:       libeconf
Requires:       libevent
Requires:       libgcc
Requires:       libidn2
Requires:       libnghttp2
Requires:       libpsl
Requires:       libselinux
Requires:       libssh
Requires:       libstdc++
Requires:       libunistring
Requires:       libuuid
Requires:       libuv
Requires:       libxcrypt
Requires:       libxml2
Requires:       libyaml
Requires:       libzstd
Requires:       lz4-libs
Requires:       ncurses-libs
Requires:       openldap
Requires:       openssh
Requires:       openssh-clients
Requires:       openssh-server
Requires:       openssl-libs
Requires:       pam
Requires:       pcre2
Requires:       perl-libs
Requires:       python3-libs
Requires:       readline
Requires:       rsync
Requires:       xz-libs
Requires:       zlib

%description
Cloudberry Database is an advanced, open-source, and highly parallel data warehouse developed from PostgreSQL and Greenplum. It offers powerful analytical capabilities and enhanced security features, making it suitable for complex data processing and analytics.

Key Features:
- Parallel query execution for optimized performance
- Robust security measures including Transparent Data Encryption (TDE)
- Integration with various ETL and BI tools
- Compatibility with multiple data sources and formats

Cloudberry Database is ideal for use cases requiring both batch processing and real-time data warehousing.

For more information, visit the official Cloudberry Database website at https://cloudberrydb.org.

%prep
%setup -q -c -T
# Ensure the target directory exists
mkdir -p %{buildroot}/usr/local
# Unpack the source tarball into the target directory
tar xzf %{SOURCE0} -C %{buildroot}/usr/local

%build
# Normally you'd run your build system here (e.g., make), but we're using the pre-built binary.

%install
rm -rf %{buildroot}

# Create the versioned directory
mkdir -p %{buildroot}/usr/local/cbdb-%{version}

# Unpack the tarball
tar xzf %{SOURCE0} -C %{buildroot}/usr/local/cbdb-%{version}

# Move the contents of the cbdb directory up one level
mv %{buildroot}/usr/local/cbdb-%{version}/cbdb/* %{buildroot}/usr/local/cbdb-%{version}/

# Remove the now-empty cbdb directory
rmdir %{buildroot}/usr/local/cbdb-%{version}/cbdb

# Create the symbolic link
ln -sfn /usr/local/cbdb-%{version} %{buildroot}/usr/local/cbdb

# No need to install LICENSE if it's already in the right place within the cbdb-1.0.0 directory

%files
/usr/local/cbdb-%{version}
/usr/local/cbdb

%license /usr/local/cbdb-%{version}/LICENSE

%postun
if [ $1 -eq 0 ] ; then
  if [ "$(readlink -f "/usr/local/cbdb")" == "/usr/local/cbdb-%{version}" ]; then
    unlink "/usr/local/cbdb" || true
  fi
fi

%changelog
* Thu Aug 16 2024 Your Name eespino@apache.gmail.com - 1.5.4-1
* Initial package with binary files under Apache 2.0 License
