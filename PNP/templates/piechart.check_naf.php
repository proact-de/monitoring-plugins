<?php
#
# Copyright (c) 2006-2010 Joerg Linge (http://www.pnp4nagios.org)
# Copyright (c) 2011 Sven Velt <sv@teamix.net>
# Copyright (c) 2011 Sebastian Harl <sh@teamix.net>
#
# Default Template used if no other template is found.

#
### Helper functions
#

require_once("check_naf_helper.php");

#
### Main loop
#

$graphs = 0;

##foreach ($this->DS as $KEY=>$VAL) {
while( count($this->DS) > 0 ) {
	$VAL = array_shift($this->DS);

	if ($VAL['NAME'] == 'nacache_usage') {
		$opt[$graphs]['title']  = "PAM cache usage on " . $this->MACRO['DISP_HOSTNAME'];
		$opt[$graphs]['labels'] = array("PAM cache usage");

		$ds_name[$graphs] = "PAM cache usage";

		# this is an percentage
		$def[$graphs] = array($VAL['ACT'], 100.0 - $VAL['ACT']);


	} elseif (substr($VAL['NAME'], 0, 8) == 'nacache_') {
		$o_hits   = $VAL;
		$o_miss   = array_shift($this->DS);
		$o_evict  = array_shift($this->DS);
		$o_inval  = array_shift($this->DS);
		$o_insert = array_shift($this->DS);

		$opt[$graphs]['title']  = "PAM ops/s on " . $this->MACRO['DISP_HOSTNAME'];
		$opt[$graphs]['labels'] = array("hits", "miss", "evict", "inval", "insert");

		$ds_name[$graphs] = "PAM ops/s";

		$def[$graphs]  = array($o_hits['ACT'], $o_miss['ACT'], $o_evict['ACT'], $o_inval['ACT'], $o_insert['ACT']);


#	} elseif ($VAL['NAME'] == 'nacpu') {
#		$opt[$graphs]  = "--vertical-label % -l 0 -r --title \"CPU usage on ";
#		$opt[$graphs] .= $this->MACRO['DISP_HOSTNAME'] . "\"";
#
#		$ds_name[$graphs] = $VAL['LABEL'];
#
#		$def[$graphs]  = "";
#		$def[$graphs] .= rrd::def     ("cpu_avg", $VAL['RRDFILE'], $VAL['DS'], "AVERAGE");
#		$def[$graphs] .= rrd::def     ("cpu_min", $VAL['RRDFILE'], $VAL['DS'], "MIN");
#		$def[$graphs] .= rrd::def     ("cpu_max", $VAL['RRDFILE'], $VAL['DS'], "MAX");
#
#		$def[$graphs] .= rrd::area    ("cpu_max", "#6666FFCC");
#		$def[$graphs] .= rrd::area    ("cpu_min", "#FFFFFF");
#		$def[$graphs] .= rrd::line1   ("cpu_avg", "#0000FF", "CPU usage:");
#
#		$def[$graphs] .= wc($VAL);
#		$def[$graphs] .= rrd::gprint  ("cpu_avg", array("LAST","MAX","AVERAGE"), "%3.4lf %S".$VAL['UNIT']);
#
#
#	} elseif ($VAL['NAME'] == 'nacs') {
#		$opt[$graphs]  = "--vertical-label \"Context Switches\" -l 0 -r --title \"Context switches on ";
#		$opt[$graphs] .= $this->MACRO['DISP_HOSTNAME'] . "\"";
#
#		$ds_name[$graphs] = $VAL['LABEL'];
#
#		$def[$graphs]  = "";
#		$def[$graphs] .= rrd::def     ("cs_avg", $VAL['RRDFILE'], $VAL['DS'], "AVERAGE");
#		$def[$graphs] .= rrd::def     ("cs_min", $VAL['RRDFILE'], $VAL['DS'], "MIN");
#		$def[$graphs] .= rrd::def     ("cs_max", $VAL['RRDFILE'], $VAL['DS'], "MAX");
#
#		$def[$graphs] .= rrd::area    ("cs_max", "#FF6666CC");
#		$def[$graphs] .= rrd::area    ("cs_min", "#FFFFFF");
#		$def[$graphs] .= rrd::line1   ("cs_avg", "#FF0000", "Context switches:");
#
#		$def[$graphs] .= wc($VAL);
#		$def[$graphs] .= rrd::gprint  ("cs_avg", array("LAST","MAX","AVERAGE"), "%3.4lf %S".$VAL['UNIT']);
#
#
#	} elseif ($VAL['NAME'] == 'nadisk_total') {
#		$d_t = $VAL;
#		$d_a = array_shift($this->DS);
#		$d_s = array_shift($this->DS);
#		$d_f = array_shift($this->DS);
#
#		$opt[$graphs]  = "--vertical-label \"Disks\" -l 0 -r --title \"Disks on ";
#		$opt[$graphs] .= $this->MACRO['DISP_HOSTNAME'] . "\"";
#
#		$ds_name[$graphs] = "Disks";
#
#		$def[$graphs]  = "";
#		$def[$graphs] .= rrd::def     ("total",  $d_t['RRDFILE'], $d_t['DS'], "MAX");
#		$def[$graphs] .= rrd::def     ("active", $d_a['RRDFILE'], $d_a['DS'], "MIN");
#		$def[$graphs] .= rrd::def     ("spare",  $d_s['RRDFILE'], $d_s['DS'], "MIN");
#		$def[$graphs] .= rrd::def     ("failed", $d_f['RRDFILE'], $d_f['DS'], "MAX");
#
#		$def[$graphs] .= rrd::line1   ("total", "#000000", "Disks total\: ");
#		$def[$graphs] .= rrd::gprint  ("total", "LAST", "%3.0lf %S\\n".$d_t['UNIT']);
#
#		$def[$graphs] .= rrd::area    ("active", "#0000FFEE", "Disks active\:");
#		$def[$graphs] .= rrd::gprint  ("active", "LAST", "%3.0lf %S\\n".$d_a['UNIT']);
#
#		$def[$graphs] .= rrd::area    ("spare", "#77FF77CC", "Disks spare\: ", "STACK");
#		$def[$graphs] .= rrd::gprint  ("spare", "LAST", "%3.0lf %S\\n".$d_s['UNIT']);
#
#		$def[$graphs] .= rrd::area    ("failed", "#FF3333", "Disks failed\:", "STACK");
#		$def[$graphs] .= rrd::gprint  ("failed", "LAST", "%3.0lf %S\\n".$d_s['UNIT']);
#
#
#	} elseif (substr($VAL['NAME'], 0, 5) == 'naio_') {
#		$io1 = $VAL;
#		$io2 = array_shift($this->DS);
#		
#		$type = substr($io1['NAME'], 5, 3);
#		$name   = 'UNKN';
#		$desc_r = 'Read ';
#		$desc_w = 'Write';
#		if ($type == 'net') {
#			$name    = 'Net';
#			$desc_r  = 'In ';
#			$desc_w  = 'Out';
#		} elseif ($type == 'dis') {
#			$name = 'Disk';
#		} elseif ($type == 'tap') {
#			$name = 'Tape';
#		} elseif ($type == 'fcp') {
#			$name = 'Fibre channel';
#		} elseif ($type == 'isc') {
#			$name = 'iSCSI';
#		}
#
#		$opt[$graphs]  = "--vertical-label \"Bytes/s\" --title \"" . $name . " I/O on ";
#		$opt[$graphs] .= $this->MACRO['DISP_HOSTNAME'] . "\"";
#
#		$ds_name[$graphs] = $io1['NAME'] . " + " . $io2['NAME'];
#
#		$def[$graphs]  = "";
#		$def[$graphs] .= rrd::def     ("ior", $io1['RRDFILE'], $io1['DS'], "AVERAGE");
#		$def[$graphs] .= rrd::def     ("iow", $io2['RRDFILE'], $io2['DS'], "AVERAGE");
#		
#		$def[$graphs] .= rrd::area    ("ior", "#00FF00", $desc_r . "\: ");
#		$def[$graphs] .= rrd::gprint  ("ior", array("LAST","MAX","AVERAGE"), "%7.2lf %SB/s");
#
#		$def[$graphs] .= rrd::line2   ("iow", "#0000FF", $desc_w . "\: ");
#		$def[$graphs] .= rrd::gprint  ("iow", array("LAST","MAX","AVERAGE"), "%7.2lf %SB/s");
#
#
#	} elseif (substr($VAL['NAME'], 0, 6) == 'naops_') {
#		$o_nfs   = $VAL;
#		$o_cifs  = array_shift($this->DS);
#		$o_http  = array_shift($this->DS);
#		$o_fcp   = array_shift($this->DS);
#		$o_iscsi = array_shift($this->DS);
#
#		$opt[$graphs]  = "--vertical-label \"Ops/s\" -l 0 -r --title \"Ops/s on ";
#		$opt[$graphs] .= $this->MACRO['DISP_HOSTNAME'] . "\"";
#
#		$ds_name[$graphs] = "Ops/s";
#
#		$def[$graphs]  = "";
#		$def[$graphs] .= rrd::def     ("nfs",   $o_nfs['RRDFILE'],   $o_nfs['DS'], "AVERAGE");
#		$def[$graphs] .= rrd::def     ("cifs",  $o_cifs['RRDFILE'],  $o_cifs['DS'], "AVERAGE");
#		$def[$graphs] .= rrd::def     ("http",  $o_http['RRDFILE'],  $o_http['DS'], "AVERAGE");
#		$def[$graphs] .= rrd::def     ("fcp",   $o_fcp['RRDFILE'],   $o_fcp['DS'], "AVERAGE");
#		$def[$graphs] .= rrd::def     ("iscsi", $o_iscsi['RRDFILE'], $o_iscsi['DS'], "AVERAGE");
#
#		$def[$graphs] .= rrd::line1   ("nfs", "#000000", "NFS   ops/s\: ");
#		$def[$graphs] .= rrd::gprint  ("nfs", array("LAST","MAX","AVERAGE"), "%7.2lf%Sops/s");
#
#		$def[$graphs] .= rrd::line1   ("cifs", "#00FFFF", "CIFS  ops/s\: ");
#		$def[$graphs] .= rrd::gprint  ("cifs", array("LAST","MAX","AVERAGE"), "%7.2lf%Sops/s");
#
#		$def[$graphs] .= rrd::line1   ("http", "#7F0000", "HTTP  ops/s\: ");
#		$def[$graphs] .= rrd::gprint  ("http", array("LAST","MAX","AVERAGE"), "%7.2lf%Sops/s");
#
#		$def[$graphs] .= rrd::line1   ("fcp", "#00FF00", "FCP   ops/s\: ");
#		$def[$graphs] .= rrd::gprint  ("fcp", array("LAST","MAX","AVERAGE"), "%7.2lf%Sops/s");
#
#		$def[$graphs] .= rrd::line1   ("iscsi", "#0000FF", "iSCSI ops/s\: ");
#		$def[$graphs] .= rrd::gprint  ("iscsi", array("LAST","MAX","AVERAGE"), "%7.2lf%Sops/s");


	} elseif (substr($VAL['NAME'], 0, 6) == 'navdu_') {
		$v_du = $VAL;
		$v_dt = array_shift($this->DS);
		$v_su = array_shift($this->DS);
		$v_st = array_shift($this->DS);

		$opt[$graphs]['title']  = substr($VAL['NAME'], 6) . " on " . $this->MACRO['DISP_HOSTNAME'];
		$opt[$graphs]['labels'] = array("used",    "free",    "over resv.", "free snap", "used snap");
		$opt[$graphs]['colors'] = array("#AAAAAA", "#00FF00", "#AA0000",    "#00FFFF",   "#0000CC");

		$ds_name[$graphs] = "Volume " . substr($VAL['NAME'], 6);

		$du   = $v_du['ACT'];
		$dt   = $v_dt['ACT'];
		$supo = $v_su['ACT'];
		$st   = $v_st['ACT'];

		$sf   = ($supo <= $st) ? $st - $supo : 0;
		$su   = ($supo >  $st) ? $st : $supo;
		$so   = ($supo >  $st) ? $supo - $st : 0;
		$df   = $dt - $du - $so;

		$def[$graphs] = array($du, $df, $so, $sf, $su);



	} elseif (substr($VAL['NAME'], 0, 6) == 'naviu_') {
		$v_iu = $VAL;
		$v_it = array_shift($this->DS);

		$opt[$graphs]['title']  = "INode usage on " . $this->MACRO['DISP_HOSTNAME'];
		$opt[$graphs]['labels'] = array("used", "");

		$ds_name[$graphs] = "INode usage on " . substr($VAL['NAME'], 6);

		$def[$graphs] = array($v_iu['ACT'], $v_it['ACT'] - $v_iu['ACT']);


	} else {
		$values = array();
		$labels = array();
		$value = -1;

		if ($VAL['MIN'] != "") {
			$value = $VAL['ACT'] - $VAL['MIN'];
		}
		else {
			$value - $VAL['ACT'];
		}
		array_push($values, $value);
		array_push($labels, $VAL['LABEL']);

		if ($VAL['MAX'] != "") {
			$value = $VAL['MAX'] - $VAL['ACT'];
			array_push($values, $value);
			array_push($labels, "");
		}
		elseif ($VAL['UNIT'] == "%%") {
			$value = 100.0 - $VAL['ACT'];
			array_push($values, $value);
			array_push($labels, "");
		}

		$def[$KEY] = $values;
		$opt[$KEY]['title'] = $this->MACRO['DISP_HOSTNAME'] . ' / ' . $this->MACRO['DISP_SERVICEDESC'];
		$opt[$KEY]['labels'] = $labels;
		$ds_name[$graphs] = $VAL['LABEL'];
	} // default

	$graphs++;
}
?>
