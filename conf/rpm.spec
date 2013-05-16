Name:      @name@
Summary:   Netflix GC Visualization
Version:   @version@
Release:   @release@
License:   NFLX
Packager:  Engineering Tools
Vendor:    Netflix, Inc.
Group:     Netflix Base
AutoReqProv: no
Requires: nflx-python-matplotlib, nflx-python-numpy, nflx-python-scipy

%description
GC Visualization
----------
@build.metadata@

%install
cat $0 > %{_topdir}/install.txt
mkdir -p $RPM_BUILD_ROOT
mv ${RPM_BUILD_DIR}/* $RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT/*

%files
%defattr(-,root,root)
/

%post
