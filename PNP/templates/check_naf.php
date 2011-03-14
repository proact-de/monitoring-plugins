<?php
#
# Copyright (c) 2006-2010 Joerg Linge (http://www.pnp4nagios.org)
# Default Template used if no other template is found.

#
### Helper functions
#

function wc($VAL) {
	$wcout = "";

	if ($VAL['WARN'] != "") {
		$wcout .= rrd::hrule($VAL['WARN'], "#FFFF00", "Warning  " . $VAL['WARN'] . "\\n");
	}
	if ($VAL['WARN_MIN'] != "") {
		$wcout .= rrd::hrule($VAL['WARN_MIN'], "#FFFF00", "Warning  (min)  " . $VAL['WARN_MIN'] . "\\n");
	}
	if ($VAL['WARN_MAX'] != "") {
		$wcout .= rrd::hrule($VAL['WARN_MAX'], "#FFFF00", "Warning  (max)  " . $VAL['WARN_MAX'] . "\\n");
	}
	if ($VAL['CRIT'] != "") {
		$wcout .= rrd::hrule($VAL['CRIT'], "#FF0000", "Critical " . $VAL['CRIT'] . "\\n");
	}
	if ($VAL['CRIT_MIN'] != "") {
		$wcout .= rrd::hrule($VAL['CRIT_MIN'], "#FF0000", "Critical (min)  " . $VAL['CRIT_MIN'] . "\\n");
	}
	if ($VAL['CRIT_MAX'] != "") {
		$wcout .= rrd::hrule($VAL['CRIT_MAX'], "#FF0000", "Critical (max)  " . $VAL['CRIT_MAX'] . "\\n");
	}

	return $wcout;
}

#
### Main loop
#

$graphs = 0;

##foreach ($this->DS as $KEY=>$VAL) {
while( count($this->DS) > 0 ) {
	$VAL = array_shift($this->DS);

	if ($VAL['NAME'] == 'nacache_usage') {
		$opt[$graphs]  = "--vertical-label \"PAM usage\" -l 0 -r --title \"PAM cache usage on ";
		$opt[$graphs] .= $this->MACRO['DISP_HOSTNAME'] . "\"";

		$ds_name[$graphs] = "PAM cache usage";

		$def[$graphs]  = "";
		$def[$graphs] .= rrd::def     ("usage", $VAL['RRDFILE'], $VAL['DS'], "AVERAGE");

		$def[$graphs] .= rrd::line2   ("usage", "#00CCCC", "PAM cache usage\:");

		$def[$graphs] .= rrd::gprint  ("usage", array("LAST","MAX","AVERAGE"), "%5.2lf%S".$VAL['UNIT']);


	} elseif (substr($VAL['NAME'], 0, 8) == 'nacache_') {
		$o_hits   = $VAL;
		$o_miss   = array_shift($this->DS);
		$o_evict  = array_shift($this->DS);
		$o_inval  = array_shift($this->DS);
		$o_insert = array_shift($this->DS);

		$opt[$graphs]  = "--vertical-label \"PAM ops/s\" --title \"PAM ops/s on ";
		$opt[$graphs] .= $this->MACRO['DISP_HOSTNAME'] . "\"";

		$ds_name[$graphs] = "PAM ops/s";

		$def[$graphs]  = "";
		$def[$graphs] .= rrd::def     ("hits",   $o_hits['RRDFILE'],   $o_hits['DS'],   "AVERAGE");
		$def[$graphs] .= rrd::def     ("miss",   $o_miss['RRDFILE'],   $o_miss['DS'],   "AVERAGE");
		$def[$graphs] .= rrd::def     ("evict",  $o_evict['RRDFILE'],  $o_evict['DS'],  "AVERAGE");
		$def[$graphs] .= rrd::def     ("inval",  $o_inval['RRDFILE'],  $o_inval['DS'],  "AVERAGE");
		$def[$graphs] .= rrd::def     ("insert", $o_insert['RRDFILE'], $o_insert['DS'], "AVERAGE");

		$def[$graphs] .= rrd::line1   ("hits", "#00CC00", "Hits\:     ");
		$def[$graphs] .= rrd::gprint  ("hits", array("LAST","MAX","AVERAGE"), "%7.2lf%Sops/s");

		$def[$graphs] .= rrd::line1   ("miss", "#CC0000", "Misses\:   ", "STACK");
		$def[$graphs] .= rrd::gprint  ("miss", array("LAST","MAX","AVERAGE"), "%7.2lf%Sops/s");

		$def[$graphs] .= rrd::line1   ("evict", "#CCCC00", "Evicts\:   ", "STACK");
		$def[$graphs] .= rrd::gprint  ("evict", array("LAST","MAX","AVERAGE"), "%7.2lf%Sops/s");

		$def[$graphs] .= rrd::line1   ("inval", "#660000", "Invalids\: ", "STACK");
		$def[$graphs] .= rrd::gprint  ("inval", array("LAST","MAX","AVERAGE"), "%7.2lf%Sops/s");

		$def[$graphs] .= rrd::line1   ("insert", "#0000FF", "Inserts\:  ", "STACK");
		$def[$graphs] .= rrd::gprint  ("insert", array("LAST","MAX","AVERAGE"), "%7.2lf%Sops/s");


	} elseif ($VAL['NAME'] == 'nacpu') {
		$opt[$graphs]  = "--vertical-label % -l 0 -r --title \"CPU usage on ";
		$opt[$graphs] .= $this->MACRO['DISP_HOSTNAME'] . "\"";

		$ds_name[$graphs] = $VAL['LABEL'];

		$def[$graphs]  = "";
		$def[$graphs] .= rrd::def     ("cpu_avg", $VAL['RRDFILE'], $VAL['DS'], "AVERAGE");
		$def[$graphs] .= rrd::def     ("cpu_min", $VAL['RRDFILE'], $VAL['DS'], "MIN");
		$def[$graphs] .= rrd::def     ("cpu_max", $VAL['RRDFILE'], $VAL['DS'], "MAX");

		$def[$graphs] .= rrd::area    ("cpu_max", "#6666FFCC");
		$def[$graphs] .= rrd::area    ("cpu_min", "#FFFFFF");
		$def[$graphs] .= rrd::line1   ("cpu_avg", "#0000FF", "CPU usage:");

		$def[$graphs] .= wc($VAL);
		$def[$graphs] .= rrd::gprint  ("cpu_avg", array("LAST","MAX","AVERAGE"), "%3.4lf %S".$VAL['UNIT']);


	} elseif ($VAL['NAME'] == 'nacs') {
		$opt[$graphs]  = "--vertical-label \"Context Switches\" -l 0 -r --title \"Context switches on ";
		$opt[$graphs] .= $this->MACRO['DISP_HOSTNAME'] . "\"";

		$ds_name[$graphs] = $VAL['LABEL'];

		$def[$graphs]  = "";
		$def[$graphs] .= rrd::def     ("cs_avg", $VAL['RRDFILE'], $VAL['DS'], "AVERAGE");
		$def[$graphs] .= rrd::def     ("cs_min", $VAL['RRDFILE'], $VAL['DS'], "MIN");
		$def[$graphs] .= rrd::def     ("cs_max", $VAL['RRDFILE'], $VAL['DS'], "MAX");

		$def[$graphs] .= rrd::area    ("cs_max", "#FF6666CC");
		$def[$graphs] .= rrd::area    ("cs_min", "#FFFFFF");
		$def[$graphs] .= rrd::line1   ("cs_avg", "#FF0000", "Context switches:");

		$def[$graphs] .= wc($VAL);
		$def[$graphs] .= rrd::gprint  ("cs_avg", array("LAST","MAX","AVERAGE"), "%3.4lf %S".$VAL['UNIT']);


	} elseif ($VAL['NAME'] == 'nadisk_total') {
		$d_t = $VAL;
		$d_a = array_shift($this->DS);
		$d_s = array_shift($this->DS);
		$d_f = array_shift($this->DS);

		$opt[$graphs]  = "--vertical-label \"Disks\" -l 0 -r --title \"Disks on ";
		$opt[$graphs] .= $this->MACRO['DISP_HOSTNAME'] . "\"";

		$ds_name[$graphs] = "Disks";

		$def[$graphs]  = "";
		$def[$graphs] .= rrd::def     ("total",  $d_t['RRDFILE'], $d_t['DS'], "MAX");
		$def[$graphs] .= rrd::def     ("active", $d_a['RRDFILE'], $d_a['DS'], "MIN");
		$def[$graphs] .= rrd::def     ("spare",  $d_s['RRDFILE'], $d_s['DS'], "MIN");
		$def[$graphs] .= rrd::def     ("failed", $d_f['RRDFILE'], $d_f['DS'], "MAX");

		$def[$graphs] .= rrd::line1   ("total", "#000000", "Disks total\: ");
		$def[$graphs] .= rrd::gprint  ("total", "LAST", "%3.0lf %S\\n".$d_t['UNIT']);

		$def[$graphs] .= rrd::area    ("active", "#0000FFEE", "Disks active\:");
		$def[$graphs] .= rrd::gprint  ("active", "LAST", "%3.0lf %S\\n".$d_a['UNIT']);

		$def[$graphs] .= rrd::area    ("spare", "#77FF77CC", "Disks spare\: ", "STACK");
		$def[$graphs] .= rrd::gprint  ("spare", "LAST", "%3.0lf %S\\n".$d_s['UNIT']);

		$def[$graphs] .= rrd::area    ("failed", "#FF3333", "Disks failed\:", "STACK");
		$def[$graphs] .= rrd::gprint  ("failed", "LAST", "%3.0lf %S\\n".$d_s['UNIT']);


	} elseif (substr($VAL['NAME'], 0, 5) == 'naio_') {
		$io1 = $VAL;
		$io2 = array_shift($this->DS);
		
		$type = substr($io1['NAME'], 5, 3);
		$name   = 'UNKN';
		$desc_r = 'Read ';
		$desc_w = 'Write';
		if ($type == 'net') {
			$name    = 'Net';
			$desc_r  = 'In ';
			$desc_w  = 'Out';
		} elseif ($type == 'dis') {
			$name = 'Disk';
		} elseif ($type == 'tap') {
			$name = 'Tape';
		} elseif ($type == 'fcp') {
			$name = 'Fibre channel';
		} elseif ($type == 'isc') {
			$name = 'iSCSI';
		}

		$opt[$graphs]  = "--vertical-label \"Bytes/s\" --title \"" . $name . " I/O on ";
		$opt[$graphs] .= $this->MACRO['DISP_HOSTNAME'] . "\"";

		$ds_name[$graphs] = $io1['NAME'] . " + " . $io2['NAME'];

		$def[$graphs]  = "";
		$def[$graphs] .= rrd::def     ("ior", $io1['RRDFILE'], $io1['DS'], "AVERAGE");
		$def[$graphs] .= rrd::def     ("iow", $io2['RRDFILE'], $io2['DS'], "AVERAGE");
		
		$def[$graphs] .= rrd::area    ("ior", "#00FF00", "FIXME In/Read\:   ");
		$def[$graphs] .= rrd::gprint  ("ior", array("LAST","MAX","AVERAGE"), "%7.2lf %SB/s");

		$def[$graphs] .= rrd::line2   ("iow", "#0000FF", "FIXME Out/Write\: ");
		$def[$graphs] .= rrd::gprint  ("iow", array("LAST","MAX","AVERAGE"), "%7.2lf %SB/s");


	} elseif (substr($VAL['NAME'], 0, 6) == 'naops_') {
		$o_nfs   = $VAL;
		$o_cifs  = array_shift($this->DS);
		$o_http  = array_shift($this->DS);
		$o_fcp   = array_shift($this->DS);
		$o_iscsi = array_shift($this->DS);

		$opt[$graphs]  = "--vertical-label \"Ops/s\" -l 0 -r --title \"Ops/s on ";
		$opt[$graphs] .= $this->MACRO['DISP_HOSTNAME'] . "\"";

		$ds_name[$graphs] = "Ops/s";

		$def[$graphs]  = "";
		$def[$graphs] .= rrd::def     ("nfs",   $o_nfs['RRDFILE'],   $o_nfs['DS'], "AVERAGE");
		$def[$graphs] .= rrd::def     ("cifs",  $o_cifs['RRDFILE'],  $o_cifs['DS'], "AVERAGE");
		$def[$graphs] .= rrd::def     ("http",  $o_http['RRDFILE'],  $o_http['DS'], "AVERAGE");
		$def[$graphs] .= rrd::def     ("fcp",   $o_fcp['RRDFILE'],   $o_fcp['DS'], "AVERAGE");
		$def[$graphs] .= rrd::def     ("iscsi", $o_iscsi['RRDFILE'], $o_iscsi['DS'], "AVERAGE");

		$def[$graphs] .= rrd::line1   ("nfs", "#000000", "NFS ops/s\:   ");
		$def[$graphs] .= rrd::gprint  ("nfs", array("LAST","MAX","AVERAGE"), "%7.2lf%Sops/s");

		$def[$graphs] .= rrd::line1   ("cifs", "#00FFFF", "CIFS ops/s\:  ");
		$def[$graphs] .= rrd::gprint  ("cifs", array("LAST","MAX","AVERAGE"), "%7.2lf%Sops/s");

		$def[$graphs] .= rrd::line1   ("http", "#7F0000", "HTTP ops/s\:  ");
		$def[$graphs] .= rrd::gprint  ("http", array("LAST","MAX","AVERAGE"), "%7.2lf%Sops/s");

		$def[$graphs] .= rrd::line1   ("fcp", "#00FF00", "FCP ops/s\:   ");
		$def[$graphs] .= rrd::gprint  ("fcp", array("LAST","MAX","AVERAGE"), "%7.2lf%Sops/s");

		$def[$graphs] .= rrd::line1   ("iscsi", "#0000FF", "iSCSI ops/s\: ");
		$def[$graphs] .= rrd::gprint  ("iscsi", array("LAST","MAX","AVERAGE"), "%7.2lf%Sops/s");


	} elseif (substr($VAL['NAME'], 0, 6) == 'navdu_') {
		$v_du = $VAL;
		$v_dt = array_shift($this->DS);
		$v_su = array_shift($this->DS);
		$v_st = array_shift($this->DS);

		$opt[$graphs]  = "--vertical-label \"Bytes\" -l 0 -r --title \"" .  substr($VAL['NAME'], 6);
		$opt[$graphs] .= " on ". $this->MACRO['DISP_HOSTNAME'] . "\"";

		$ds_name[$graphs] = "Volume " . substr($VAL['NAME'], 6);

		$def[$graphs]  = "";
		$def[$graphs] .= rrd::def     ("du", $v_du['RRDFILE'], $v_du['DS'], "AVERAGE");
		$def[$graphs] .= rrd::def     ("dt", $v_dt['RRDFILE'], $v_dt['DS'], "AVERAGE");
		$def[$graphs] .= rrd::def     ("supo", $v_su['RRDFILE'], $v_su['DS'], "AVERAGE");
		$def[$graphs] .= rrd::def     ("st", $v_st['RRDFILE'], $v_st['DS'], "AVERAGE");

		$def[$graphs] .= rrd::cdef    ("vt", "dt,st,+");
		$def[$graphs] .= rrd::cdef    ("sf", "supo,st,LE,st,supo,-,0,IF");
		$def[$graphs] .= rrd::cdef    ("su", "supo,st,GT,st,supo,IF");
		$def[$graphs] .= rrd::cdef    ("so", "supo,st,GT,supo,st,-,0,IF");
		$def[$graphs] .= rrd::cdef    ("df", "dt,du,-,so,-");


		$def[$graphs] .= rrd::line1   ("vt", "#000000", "Whole Volume     ");
		$def[$graphs] .= rrd::gprint  ("vt", array("LAST","MAX","AVERAGE"), "%6.2lf%S", "\\n");

		$def[$graphs] .= rrd::area    ("du", "#AAAAAA", "Data\: used space ");
		$def[$graphs] .= rrd::gprint  ("du", array("LAST","MAX","AVERAGE"), "%6.2lf%S", "\\n");

		$def[$graphs] .= rrd::area    ("df", "#00FF00", "Data\: free space ", "STACK");
		$def[$graphs] .= rrd::gprint  ("df", array("LAST","MAX","AVERAGE"), "%6.2lf%S", "\\n");

		$def[$graphs] .= rrd::area    ("so", "#AA0000", "Snap\: over resv. ", "STACK");
		$def[$graphs] .= rrd::gprint  ("so", array("LAST","MAX","AVERAGE"), "%6.2lf%S", "\\n");

		$def[$graphs] .= rrd::area    ("sf", "#00FFFF", "Snap\: free space ", "STACK");
		$def[$graphs] .= rrd::gprint  ("sf", array("LAST","MAX","AVERAGE"), "%6.2lf%S", "\\n");

		$def[$graphs] .= rrd::area    ("su", "#0000CC", "Snap\: used space ", "STACK");
		$def[$graphs] .= rrd::gprint  ("su", array("LAST","MAX","AVERAGE"), "%6.2lf%S", "\\n");



	} elseif (substr($VAL['NAME'], 0, 6) == 'naviu_') {
		$v_iu = $VAL;
		$v_it = array_shift($this->DS);

		$opt[$graphs]  = "--vertical-label \"INodes\" -l 0 -r --title \"INode usage on ";
		$opt[$graphs] .= $this->MACRO['DISP_HOSTNAME'] . "\"";

		$ds_name[$graphs] = "INode usage on " . substr($VAL['NAME'], 6);

		$def[$graphs]  = "";
		$def[$graphs] .= rrd::def     ("iu", $v_iu['RRDFILE'], $v_iu['DS'], "AVERAGE");
		$def[$graphs] .= rrd::def     ("it", $v_it['RRDFILE'], $v_it['DS'], "AVERAGE");

		$def[$graphs] .= rrd::area    ("it", "#00FF00");
		$def[$graphs] .= rrd::line1   ("it", "#000000");
		$def[$graphs] .= rrd::area    ("iu", "#0000FF", "INodes used\: ");
		$def[$graphs] .= rrd::gprint  ("iu", array("LAST","MAX","AVERAGE"), "%7.2lf%S");
		$def[$graphs] .= wc($v_iu);



	} else {
		$vlabel   = "";
		$lower    = "";
		$upper    = "";
		
		if ($VAL['MIN'] != "") {
			$lower = " --lower=" . $VAL['MIN'];
		}
		if ($VAL['UNIT'] == "%%") {
			$vlabel = "%";
			$upper = " --upper=101 ";
			$lower = " --lower=0 ";
		}
		else {
			$vlabel = $VAL['UNIT'];
		}

		$opt[$graphs] = '--vertical-label "' . $vlabel . '" --title "' . $this->MACRO['DISP_HOSTNAME'] . ' / ' . $this->MACRO['DISP_SERVICEDESC'] . '"' . $upper . $lower;
		$ds_name[$graphs] = $VAL['LABEL'];
		$def[$graphs]  = rrd::def     ("var1", $VAL['RRDFILE'], $VAL['DS'], "AVERAGE");
		$def[$graphs] .= rrd::gradient("var1", "BDC6DE", "3152A5", rrd::cut($VAL['NAME'],16), 20);
		$def[$graphs] .= rrd::line1   ("var1", "#000000" );
		$def[$graphs] .= rrd::gprint  ("var1", array("LAST","MAX","AVERAGE"), "%3.4lf %S".$VAL['UNIT']);
		$def[$graphs] .= wc($VAL);
		$def[$graphs] .= rrd::comment("Command " . $VAL['TEMPLATE'] . " - " . $VAL['NAME'] . "\\r");
	} // default

	$graphs++;
}
?>
