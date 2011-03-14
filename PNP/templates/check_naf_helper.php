<?

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

?>
