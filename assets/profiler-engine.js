/* ════════════════════════════════════════════════════════════════════════
   Fair Code - Dataset Profiler ENGINE (browser port of faircode/profiler.py)

   This is a faithful JavaScript port of faircode/SPEC.md. It MUST produce the
   same numbers as the Python CLI for the same CSV. All analysis runs locally
   in the browser - the file never leaves the visitor's machine.

   Exposes window.FairCodeProfiler = { parseCSV, profile }.
   ════════════════════════════════════════════════════════════════════════ */
(function (global) {
  'use strict';

  // ── Defaults (SPEC section 7) ──────────────────────────────────────────
  var MIN_SHARE_THRESHOLD = 0.05;
  var INTERSECTION_FLOOR = 0.01;
  var IMBALANCE_FLAG = 3.0;
  var MISSING_FLAG = 0.05;
  var AGE_BANDS = [0, 18, 30, 45, 60, 75];
  var MAX_CATEGORICAL_CARD = 20;
  var MAX_DIMENSION_GROUPS = 50;

  // Pandas-style missing tokens, so JS null-handling matches read_csv defaults.
  var NA_TOKENS = { '': 1, 'na': 1, 'n/a': 1, 'nan': 1, 'null': 1, 'none': 1 };

  // ── Keyword lists - MUST mirror faircode/detect.py ─────────────────────
  var KEYWORDS = [
    ['sex', ['sex', 'gender']],
    ['race', ['race', 'ethnic', 'ethnicity']],
    ['age', ['age', 'dob', 'yob', 'birth']],
    ['geography', ['region', 'state', 'zip', 'zipcode', 'postal', 'country',
                   'county', 'city', 'location', 'province']]
  ];

  var DATE_RE = /\d{1,4}[/-]\d{1,2}[/-]\d{1,4}/;

  // ── CSV parsing ────────────────────────────────────────────────────────
  // Handles quoted fields, escaped quotes (""), and newlines inside quotes.
  function parseCSV(text) {
    if (text.charCodeAt(0) === 0xFEFF) text = text.slice(1); // strip BOM
    var rows = [], field = '', row = [], inQuotes = false;
    for (var i = 0; i < text.length; i++) {
      var c = text[i];
      if (inQuotes) {
        if (c === '"') {
          if (text[i + 1] === '"') { field += '"'; i++; }
          else inQuotes = false;
        } else field += c;
      } else if (c === '"') {
        inQuotes = true;
      } else if (c === ',') {
        row.push(field); field = '';
      } else if (c === '\n' || c === '\r') {
        if (c === '\r' && text[i + 1] === '\n') i++;
        row.push(field); field = '';
        if (row.length > 1 || row[0] !== '') rows.push(row);
        row = [];
      } else field += c;
    }
    if (field !== '' || row.length) { row.push(field); rows.push(row); }
    if (!rows.length) return { columns: [], rows: [] };

    var columns = rows[0];
    var data = [];
    for (var r = 1; r < rows.length; r++) {
      var obj = {};
      for (var ci = 0; ci < columns.length; ci++) {
        var raw = rows[r][ci];
        raw = raw === undefined ? '' : raw;
        obj[columns[ci]] = isMissing(raw) ? null : raw;
      }
      data.push(obj);
    }
    return { columns: columns, rows: data };
  }

  function isMissing(v) {
    if (v === null || v === undefined) return true;
    return NA_TOKENS.hasOwnProperty(String(v).trim().toLowerCase());
  }

  // ── Column detection (SPEC section 1) ──────────────────────────────────
  function tokens(name) {
    var spaced = String(name).replace(/([a-z0-9])([A-Z])/g, '$1 $2');
    return spaced.split(/[^A-Za-z0-9]+/).filter(Boolean).map(function (t) {
      return t.toLowerCase();
    });
  }

  function tokenMatches(token, keyword) {
    if (keyword.length < 4) return token === keyword;
    return token.indexOf(keyword) === 0; // prefix match
  }

  function classifyName(name) {
    var toks = tokens(name);
    for (var k = 0; k < KEYWORDS.length; k++) {
      var kind = KEYWORDS[k][0], words = KEYWORDS[k][1];
      for (var t = 0; t < toks.length; t++) {
        for (var w = 0; w < words.length; w++) {
          if (tokenMatches(toks[t], words[w])) return kind;
        }
      }
    }
    return null;
  }

  function nunique(rows, col) {
    var seen = {};
    for (var i = 0; i < rows.length; i++) {
      var v = rows[i][col];
      if (v !== null) seen[v] = 1;
    }
    return Object.keys(seen).length;
  }

  function detectColumns(table) {
    var detected = [];
    table.columns.forEach(function (col) {
      var kind = classifyName(col);
      if (kind !== null) { detected.push({ name: col, kind: kind }); return; }
      var n = nunique(table.rows, col);
      if (n >= 2 && n <= MAX_CATEGORICAL_CARD) {
        detected.push({ name: col, kind: 'categorical' });
      }
    });
    return detected;
  }

  // ── Age handling (SPEC section 2) ──────────────────────────────────────
  function ageToNumeric(value) {
    if (value === null || value === undefined) return null;
    if (typeof value === 'number') return value;
    var m = String(value).match(/\d+/);
    return m ? parseFloat(m[0]) : null;
  }

  function ageBand(num) {
    if (num === null) return null;
    for (var i = 0; i < AGE_BANDS.length - 1; i++) {
      if (num >= AGE_BANDS[i] && num < AGE_BANDS[i + 1]) {
        return AGE_BANDS[i] + '-' + AGE_BANDS[i + 1];
      }
    }
    return AGE_BANDS[AGE_BANDS.length - 1] + '+';
  }

  function looksLikeDates(rows, col) {
    var sample = [], i;
    for (i = 0; i < rows.length && sample.length < 50; i++) {
      if (rows[i][col] !== null) sample.push(String(rows[i][col]));
    }
    if (!sample.length) return false;
    var hits = 0;
    for (i = 0; i < sample.length; i++) if (DATE_RE.test(sample[i])) hits++;
    return hits / sample.length > 0.5;
  }

  function skewness(values) {
    var n = values.length;
    if (n < 3) return null;
    var mean = 0, i;
    for (i = 0; i < n; i++) mean += values[i];
    mean /= n;
    var m2 = 0, m3 = 0, d;
    for (i = 0; i < n; i++) { d = values[i] - mean; m2 += d * d; m3 += d * d * d; }
    m2 /= n; m3 /= n;
    if (m2 === 0) return null;
    return m3 / Math.pow(m2, 1.5);
  }

  function round(x, dp) {
    var f = Math.pow(10, dp || 0);
    return Math.round(x * f) / f;
  }

  // ── Per-dimension metrics (SPEC section 3) ─────────────────────────────
  function analyzeGroups(counts, nTotal, nullCount, skew) {
    var labels = Object.keys(counts);
    var nNonnull = 0, i;
    for (i = 0; i < labels.length; i++) nNonnull += counts[labels[i]];

    var groups = labels.map(function (label) {
      return { label: String(label), count: counts[label],
               share: nNonnull ? counts[label] / nNonnull : 0 };
    });
    // count desc, then label asc - deterministic tie-break to match Python.
    groups.sort(function (a, b) {
      return (b.count - a.count) ||
             (a.label < b.label ? -1 : a.label > b.label ? 1 : 0);
    });

    var shares = groups.map(function (g) { return g.share; });
    var k = shares.length;
    var minShare = k ? Math.min.apply(null, shares) : 0;
    var maxShare = k ? Math.max.apply(null, shares) : 0;
    var imbalance = minShare > 0 ? maxShare / minShare : Infinity;

    var entropyRatio;
    if (k <= 1) {
      entropyRatio = 0;
    } else {
      var H = 0;
      for (i = 0; i < shares.length; i++) {
        if (shares[i] > 0) H -= shares[i] * Math.log(shares[i]);
      }
      entropyRatio = H / Math.log(k);
    }

    var under = groups.filter(function (g) { return g.share < MIN_SHARE_THRESHOLD; })
                      .map(function (g) { return g.label; });

    return {
      n_groups: k,
      dimension_score: Math.round(entropyRatio * 100),
      entropy_ratio: round(entropyRatio, 4),
      imbalance_ratio: imbalance === Infinity ? null : round(imbalance, 2),
      min_share: round(minShare, 4),
      missing_pct: nTotal ? round(nullCount / nTotal, 4) : 0,
      skewness: skew === null || skew === undefined ? null : round(skew, 4),
      groups: groups.map(function (g) {
        return { label: g.label, count: g.count, share: g.share };
      }),
      under_represented: under
    };
  }

  function dimension(table, name, kind) {
    var rows = table.rows, nTotal = rows.length, i, v;

    if (kind === 'age' && !looksLikeDates(rows, name)) {
      var nums = [], numericVals = [];
      for (i = 0; i < nTotal; i++) {
        var num = ageToNumeric(rows[i][name]);
        nums.push(num);
        if (num !== null) numericVals.push(num);
      }
      if (numericVals.length) {
        var skew = skewness(numericVals);
        var counts = {}, nullCount = 0;
        for (i = 0; i < nums.length; i++) {
          var b = ageBand(nums[i]);
          if (b === null) nullCount++;
          else counts[b] = (counts[b] || 0) + 1;
        }
        var res = analyzeGroups(counts, nTotal, nullCount, skew);
        res.name = name; res.kind = kind;
        return res;
      }
    }

    // Categorical path.
    var c = {}, nulls = 0;
    for (i = 0; i < nTotal; i++) {
      v = rows[i][name];
      if (v === null) nulls++;
      else c[v] = (c[v] || 0) + 1;
    }
    var r = analyzeGroups(c, nTotal, nulls, null);
    r.name = name; r.kind = kind;
    return r;
  }

  // ── Intersectional gaps (SPEC section 4) ───────────────────────────────
  function labelize(table, name, kind) {
    var rows = table.rows, out = [], i;
    if (kind === 'age' && !looksLikeDates(rows, name)) {
      var any = false;
      for (i = 0; i < rows.length; i++) {
        if (ageToNumeric(rows[i][name]) !== null) { any = true; break; }
      }
      if (any) {
        for (i = 0; i < rows.length; i++) out.push(ageBand(ageToNumeric(rows[i][name])));
        return out;
      }
    }
    for (i = 0; i < rows.length; i++) out.push(rows[i][name]);
    return out;
  }

  function intersections(table, dims) {
    if (dims.length < 2) return [];
    var a = dims[0], b = dims[1];
    var nTotal = table.rows.length;
    var floor = INTERSECTION_FLOOR * nTotal;
    var la = labelize(table, a.name, a.kind);
    var lb = labelize(table, b.name, b.kind);

    var ct = {}, aVals = {}, bVals = {}, i, key;
    for (i = 0; i < nTotal; i++) {
      if (la[i] === null || lb[i] === null) continue;
      aVals[la[i]] = 1; bVals[lb[i]] = 1;
      key = la[i] + ' ' + lb[i];
      ct[key] = (ct[key] || 0) + 1;
    }
    var cells = [];
    Object.keys(aVals).forEach(function (av) {
      Object.keys(bVals).forEach(function (bv) {
        var count = ct[av + ' ' + bv] || 0;
        if (count === 0 || count < floor) {
          cells.push({ a: String(av), b: String(bv), count: count });
        }
      });
    });
    if (!cells.length) return [];
    cells.sort(function (x, y) {  // deterministic order, matches Python
      return x.a < y.a ? -1 : x.a > y.a ? 1 : (x.b < y.b ? -1 : x.b > y.b ? 1 : 0);
    });
    return [{ dims: [a.name, b.name], cells: cells }];
  }

  // ── Flags + grade (SPEC sections 5 & 6) ────────────────────────────────
  function grade(score) {
    if (score >= 85) return 'A';
    if (score >= 70) return 'B';
    if (score >= 55) return 'C';
    if (score >= 40) return 'D';
    return 'F';
  }

  function buildFlags(dimensions, inters) {
    var flags = [];
    dimensions.forEach(function (d) {
      d.groups.forEach(function (g) {
        if (d.under_represented.indexOf(g.label) !== -1) {
          flags.push(d.name + ": '" + g.label + "' is under-represented (" +
                     (g.share * 100).toFixed(1) + '%)');
        }
      });
      if (d.imbalance_ratio !== null && d.imbalance_ratio >= IMBALANCE_FLAG) {
        flags.push(d.name + ': imbalance ratio ' + d.imbalance_ratio.toFixed(1) +
                   '× between largest and smallest group');
      } else if (d.imbalance_ratio === null && d.n_groups > 1) {
        flags.push(d.name + ': a subgroup is effectively absent (0 rows)');
      }
      if (d.missing_pct >= MISSING_FLAG) {
        flags.push(d.name + ': ' + (d.missing_pct * 100).toFixed(1) +
                   '% of values are missing');
      }
    });
    inters.forEach(function (inter) {
      var a = inter.dims[0], b = inter.dims[1];
      inter.cells.forEach(function (cell) {
        var kind = cell.count === 0 ? 'absent' : 'only ' + cell.count + ' rows';
        flags.push(a + "='" + cell.a + "' × " + b + "='" + cell.b + "' is " + kind);
      });
    });
    return flags;
  }

  // ── Public entry point ─────────────────────────────────────────────────
  function profile(table) {
    var detected = detectColumns(table);
    var dimensions = detected.map(function (d) {
      return dimension(table, d.name, d.kind);
    });
    dimensions = dimensions.filter(function (d) {
      return d.kind === 'geography' || d.n_groups <= MAX_DIMENSION_GROUPS;
    });
    var keptNames = {};
    dimensions.forEach(function (d) { keptNames[d.name] = 1; });
    detected = detected.filter(function (d) { return keptNames[d.name]; });

    var inters = intersections(table, detected);

    var overall = 0;
    if (dimensions.length) {
      var sum = 0;
      dimensions.forEach(function (d) { sum += d.dimension_score; });
      overall = Math.round(sum / dimensions.length);
    }

    return {
      n_rows: table.rows.length,
      n_cols: table.columns.length,
      overall_score: overall,
      grade: grade(overall),
      dimensions: dimensions,
      intersections: inters,
      flags: buildFlags(dimensions, inters)
    };
  }

  global.FairCodeProfiler = { parseCSV: parseCSV, profile: profile };
})(typeof globalThis !== 'undefined' ? globalThis : this);
