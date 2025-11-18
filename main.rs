use clap::Parser;
use quick_xml::events::Event;
use quick_xml::Reader;
use regex::Regex;
use serde::{Deserialize, Serialize};
use serde_json::json;
use std::collections::HashSet;
use std::fs;
use std::io::{self, BufRead};
use std::path::{Path, PathBuf};
use walkdir::WalkDir;

/// CLI arguments
#[derive(Parser, Debug)]
#[command(author, version, about = "Step1 Text Extractor - Rust", long_about = None)]
struct Args {
    /// Local path to repository or git URL (http/https/git@)
    path: String,

    /// Output JSON file (default: license_candidates.json)
    #[arg(short, long, default_value = "license_candidates.json")]
    out: String,

    /// Write JSONL (one block per line)
    #[arg(long, default_value_t = false)]
    jsonl: bool,

    /// Limit number of extracted blocks (for debugging)
    #[arg(long, default_value_t = 0)]
    max_blocks: usize,
}

/// Output block structure
#[derive(Debug, Serialize, Deserialize, Clone)]
struct Block {
    source: String,
    file_path: String,
    block_type: String,
    start_line: Option<usize>,
    end_line: Option<usize>,
    raw_text: String,
    text: String,
    extracted_by: String,
    repo_root: String,
    word_count: usize,
    contains_license_keyword: bool,
}

fn is_binary_file(path: &Path) -> bool {
    if let Ok(mut f) = fs::File::open(path) {
        use std::io::Read;
        let mut buf = [0u8; 4096];
        if let Ok(n) = f.read(&mut buf) {
            return buf[..n].contains(&0u8);
        }
    }
    // fallback: treat unreadable files as binary to skip
    true
}

/// Simple textual normalization: strip comment prefixes and collapse whitespace
fn normalize_text_block(text: &str, preserve_case: bool) -> String {
    let mut lines: Vec<String> = text
        .lines()
        .map(|ln| {
            let mut s = ln.trim_start().to_string();

            // strip common prefixes
            if s.starts_with("//") {
                s = s[2..].trim_start().to_string();
            }
            if s.starts_with('#') {
                s = s[1..].trim_start().to_string();
            }
            if s.starts_with("/*") {
                s = s[2..].trim_start().to_string();
            }
            if s.ends_with("*/") {
                s = s[..s.len() - 2].trim_end().to_string();
            }
            if s.starts_with('*') {
                s = s[1..].trim_start().to_string();
            }
            s
        })
        .collect();

    // join and normalize whitespace
    let mut cleaned = lines.join("\n");
    // normalize CRLF -> LF
    cleaned = cleaned.replace("\r\n", "\n").replace('\r', "\n");
    // collapse repeated spaces
    let re_spaces = Regex::new(r"[ \t]+").unwrap();
    cleaned = re_spaces.replace_all(&cleaned, " ").to_string();
    // collapse multiple newlines
    let re_newlines = Regex::new(r"\n{3,}").unwrap();
    cleaned = re_newlines.replace_all(&cleaned, "\n\n").to_string();

    if !preserve_case {
        cleaned = cleaned.to_lowercase();
    }

    cleaned.trim().to_string()
}

fn contains_license_keywords(text: &str) -> bool {
    // set of heuristics keywords (lowercase)
    const KW: [&str; 9] = [
        "permission is hereby granted",
        "licensed under the",
        "gnu general public license",
        "redistribution and use",
        "without warranty",
        "copyright",
        "spdx-license-identifier",
        "spdx",
        "mit license",
    ];
    let t = text.to_lowercase();
    for k in &KW {
        if t.contains(k) {
            return true;
        }
    }
    false
}

fn find_license_files(repo_root: &Path) -> Vec<PathBuf> {
    let mut results = Vec::new();
    let top_entries = fs::read_dir(repo_root)
        .map(|rd| rd.filter_map(Result::ok).collect::<Vec<_>>())
        .unwrap_or_default();
    let license_names: HashSet<&str> = [
        "license",
        "license.txt",
        "license.md",
        "copying",
        "unlicense",
        "notice",
        "copyright",
        "legal",
    ]
    .iter()
    .cloned()
    .collect();

    for ent in top_entries {
        if ent.file_type().map(|ft| ft.is_file()).unwrap_or(false) {
            let name = ent.file_name().to_string_lossy().to_lowercase();
            if license_names.contains(name.as_str()) {
                results.push(ent.path());
            }
        }
    }

    for entry in WalkDir::new(repo_root)
        .follow_links(true)
        .into_iter()
        .filter_map(Result::ok)
    {
        if !entry.file_type().is_file() {
            continue;
        }
        let name = entry.file_name().to_string_lossy().to_lowercase();
        if ["notice", "copying", "license.txt", "license.md", "unlicense"].contains(&name.as_str()) {
            if !results.contains(&entry.path().to_path_buf()) {
                results.push(entry.path().to_path_buf());
            }
        }
    }

    results
}

fn safe_read_text(path: &Path) -> Option<String> {
    // Try utf-8, fallback to lossly UTF-8
    match fs::read(path) {
        Ok(bytes) => Some(String::from_utf8_lossy(&bytes).to_string()),
        Err(_) => None,
    }
}

fn extract_full_license_blocks(paths: Vec<PathBuf>, repo_root: &Path) -> Vec<Block> {
    let mut blocks = Vec::new();

    for p in paths {
        if let Some(txt) = safe_read_text(&p) {
            let norm = normalize_text_block(&txt, true);
            let wc = norm.split_whitespace().count();
            blocks.push(Block {
                source: p.to_string_lossy().to_string(),
                file_path: p.to_string_lossy().to_string(),
                block_type: "full_license".to_string(),
                start_line: Some(1),
                end_line: Some(txt.lines().count()),
                raw_text: txt,
                text: norm,
                extracted_by: "step1_text_extractor_rust".to_string(),
                repo_root: repo_root.to_string_lossy().to_string(),
                word_count: wc,
                contains_license_keyword: contains_license_keywords(&norm),
            })
        }
    }

    blocks
}

fn extract_header_comment_blocks(repo_root: &Path) -> Vec<Block> {
    // Source file ext set (lowercase)
    let exts: HashSet<&str> = [
        ".py", ".js", ".ts", ".java", ".c", ".cpp", ".cc", ".h", ".hpp", ".go", ".rs", ".rb", ".php",
        ".scala", ".swift", ".kt", ".kts",
    ]
    .iter()
    .cloned()
    .collect();

    let mut blocks = Vec::new();

    for entry in WalkDir::new(repo_root).into_iter().filter_map(Result::ok) {
        if !entry.file_type().is_file() {
            continue;
        }
        let path = entry.path().to_path_buf();

        if let Some(sfx) = path.extension().and_then(|e| e.to_str()) {
            let dot_ext = format!(".{}", sfx).to_lowercase();
            if !exts.contains(dot_ext.as_str()) {
                continue;
            }

            // try to read header
            if is_binary_file(&path) {
                continue;
            }
            if let Some(text) = safe_read_text(&path) {
                // limit to first N lines
                const HEADER_MAX_LINES: usize = 200;
                let first_lines: String = text
                    .lines()
                    .take(HEADER_MAX_LINES)
                    .collect::<Vec<&str>>()
                    .join("\n");

                // Attempt multi-line comment extraction and single-line prefixes
                // naive multi-line block detection
                let mut header_candidate = String::new();

                // try /* ... */ style
                if let Some(open_pos) = first_lines.find("/*") {
                    if let Some(close_pos) = first_lines[open_pos..].find("*/") {
                        header_candidate =
                            first_lines[open_pos..open_pos + close_pos + "*/".len()].to_string();
                    }
                }

                // try triple quotes for python
                if header_candidate.is_empty() {
                    if let Some(open_pos) = first_lines.find("'''") {
                        if let Some(close_pos) = first_lines[open_pos + 3..].find("'''") {
                            header_candidate =
                                first_lines[open_pos..open_pos + 3 + close_pos + 3].to_string();
                        }
                    }
                    if header_candidate.is_empty() {
                        if let Some(open_pos) = first_lines.find("\"\"\"") {
                            if let Some(close_pos) = first_lines[open_pos + 3..].find("\"\"\"") {
                                header_candidate =
                                    first_lines[open_pos..open_pos + 3 + close_pos + 3].to_string();
                            }
                        }
                    }
                }

                // fallback: collect consecutive single-line comment lines starting at top
                if header_candidate.is_empty() {
                    let mut collected: Vec<String> = vec![];
                    for ln in first_lines.lines() {
                        let trimmed = ln.trim_start();
                        if trimmed.starts_with("//") || trimmed.starts_with('#') {
                            collected.push(ln.to_string());
                        } else if collected.is_empty() && trimmed.is_empty() {
                            // allow leading empty lines
                            continue;
                        } else if !collected.is_empty() {
                            // stop at first non-comment line after collecting some
                            break;
                        } else {
                            // not a comment start, skip
                            break;
                        }
                    }
                    header_candidate = collected.join("\n");
                }

                if header_candidate.trim().is_empty() {
                    // as a last resort, search for lines containing license keywords in first_lines
                    let mut collected: Vec<String> = vec![];
                    for ln in first_lines.lines() {
                        if contains_license_keywords(ln) {
                            collected.push(ln.to_string());
                        } else if !collected.is_empty() && ln.trim().is_empty() {
                            collected.push(ln.to_string());
                        } else if !collected.is_empty() {
                            break;
                        }
                    }
                    header_candidate = collected.join("\n");
                }

                if !header_candidate.trim().is_empty() {
                    let norm = normalize_text_block(&header_candidate, true);
                    if norm.len() >= 10 {
                        // filter tiny non-license headers
                        let wc = norm.split_whitespace().count();
                        if contains_license_keywords(&norm) || wc >= 6 {
                            blocks.push(Block {
                                source: path.to_string_lossy().to_string(),
                                file_path: path.to_string_lossy().to_string(),
                                block_type: "header_comment".to_string(),
                                start_line: Some(1),
                                end_line: Some(HEADER_MAX_LINES.min(text.lines().count())),
                                raw_text: header_candidate.clone(),
                                text: norm.clone(),
                                extracted_by: "step1_text_extractor_rust".to_string(),
                                repo_root: repo_root.to_string_lossy().to_string(),
                                word_count: wc,
                                contains_license_keyword: contains_license_keywords(&norm),
                            })
                        }
                    }
                }
            }
        }
    }

    blocks
}

fn parse_package_json(path: &Path) -> Option<Block> {
    if let Ok(txt) = fs::read_to_string(path) {
        if let Ok(v) = serde_json::from_str::<serde_json::Value>(&txt) {
            if let Some(license) = v.get("license") {
                if license.is_string() {
                    let s = license.as_str().unwrap().to_string();
                    let norm = normalize_text_block(&s, true);
                    return Some(Block {
                        source: path.to_string_lossy().to_string(),
                        file_path: path.to_string_lossy().to_string(),
                        block_type: "metadata_license_field".to_string(),
                        start_line: None,
                        end_line: None,
                        raw_text: s.clone(),
                        text: norm.clone(),
                        extracted_by: "step1_text_extractor_rust".to_string(),
                        repo_root: path
                            .parent()
                            .map(|p| p.to_string_lossy().to_string())
                            .unwrap_or_default(),
                        word_count: norm.split_whitespace().count(),
                        contains_license_keyword: contains_license_keywords(&norm),
                    });
                } else if license.is_object() {
                    // {"type":"MIT"}
                    if let Some(t) = license.get("type").and_then(|x| x.as_str()) {
                        let norm = normalize_text_block(t, true);
                        return Some(Block {
                            source: path.to_string_lossy().to_string(),
                            file_path: path.to_string_lossy().to_string(),
                            block_type: "metadata_license_field".to_string(),
                            start_line: None,
                            end_line: None,
                            raw_text: t.to_string(),
                            text: norm.clone(),
                            extracted_by: "step1_text_extractor_rust".to_string(),
                            repo_root: path
                                .parent()
                                .map(|p| p.to_string_lossy().to_string())
                                .unwrap_or_default(),
                            word_count: norm.split_whitespace().count(),
                            contains_license_keyword: contains_license_keywords(&norm),
                        });
                    }
                }
            }
        }
    }
    None
}

fn parse_pyproject_toml(path: &Path) -> Option<Block> {
    if let Ok(txt) = fs::read_to_string(path) {
        if let Ok(v) = toml::from_str::<toml::Value>(&txt) {
            if let Some(project) = v.get("project") {
                if let Some(lic) = project.get("license") {
                    match lic {
                        toml::Value::String(s) => {
                            let norm = normalize_text_block(s, true);
                            return Some(Block {
                                source: path.to_string_lossy().to_string(),
                                file_path: path.to_string_lossy().to_string(),
                                block_type: "metadata_license_field".to_string(),
                                start_line: None,
                                end_line: None,
                                raw_text: s.to_string(),
                                text: norm.clone(),
                                extracted_by: "step1_text_extractor_rust".to_string(),
                                repo_root: path
                                    .parent()
                                    .map(|p| p.to_string_lossy().to_string())
                                    .unwrap_or_default(),
                                word_count: norm.split_whitespace().count(),
                                contains_license_keyword: contains_license_keywords(&norm),
                            });
                        }
                        toml::Value::Table(tbl) => {
                            if let Some(text_val) = tbl.get("text").and_then(|x| x.as_str()) {
                                let norm = normalize_text_block(text_val, true);
                                return Some(Block {
                                    source: path.to_string_lossy().to_string(),
                                    file_path: path.to_string_lossy().to_string(),
                                    block_type: "metadata_license_field".to_string(),
                                    start_line: None,
                                    end_line: None,
                                    raw_text: text_val.to_string(),
                                    text: norm.clone(),
                                    extracted_by: "step1_text_extractor_rust".to_string(),
                                    repo_root: path
                                        .parent()
                                        .map(|p| p.to_string_lossy().to_string())
                                        .unwrap_or_default(),
                                    word_count: norm.split_whitespace().count(),
                                    contains_license_keyword: contains_license_keywords(&norm),
                                });
                            }
                        }
                        _ => {}
                    }
                }
                if let Some(lic_expr) = project.get("license-expression").and_then(|x| x.as_str()) {
                    let norm = normalize_text_block(lic_expr, true);
                    return Some(Block {
                        source: path.to_string_lossy().to_string(),
                        file_path: path.to_string_lossy().to_string(),
                        block_type: "metadata_license_field".to_string(),
                        start_line: None,
                        end_line: None,
                        raw_text: lic_expr.to_string(),
                        text: norm.clone(),
                        extracted_by: "step1_text_extractor_rust".to_string(),
                        repo_root: path
                            .parent()
                            .map(|p| p.to_string_lossy().to_string())
                            .unwrap_or_default(),
                        word_count: norm.split_whitespace().count(),
                        contains_license_keyword: contains_license_keywords(&norm),
                    });
                }
            }
        }
    }
    None
}

fn parse_cargo_toml(path: &Path) -> Option<Block> {
    if let Ok(txt) = fs::read_to_string(path) {
        if let Ok(v) = toml::from_str::<toml::Value>(&txt) {
            if let Some(pkg) = v.get("package") {
                if let Some(lic) = pkg.get("license").and_then(|x| x.as_str()) {
                    let norm = normalize_text_block(lic, true);
                    return Some(Block {
                        source: path.to_string_lossy().to_string(),
                        file_path: path.to_string_lossy().to_string(),
                        block_type: "metadata_license_field".to_string(),
                        start_line: None,
                        end_line: None,
                        raw_text: lic.to_string(),
                        text: norm.clone(),
                        extracted_by: "step1_text_extractor_rust".to_string(),
                        repo_root: path
                            .parent()
                            .map(|p| p.to_string_lossy().to_string())
                            .unwrap_or_default(),
                        word_count: norm.split_whitespace().count(),
                        contains_license_keyword: contains_license_keywords(&norm),
                    });
                }
            }
        }
    }
    None
}

fn parse_pom_xml(path: &Path) -> Option<Block> {
    if let Ok(txt) = fs::read_to_string(path) {
        // Use quick-xml to parse and find <license><name> ... </name>
        let mut reader = Reader::from_str(&txt);
        reader.trim_text(true);
        let mut buf = Vec::new();
        let mut found_license = false;
        let mut in_name = false;
        let mut license_name = None;
        loop {
            match reader.read_event(&mut buf) {
                Ok(Event::Start(ref e)) => {
                    let tag = String::from_utf8_lossy(e.name()).to_lowercase();
                    if tag.ends_with("license") || tag.ends_with("licenses") {
                        found_license = true;
                    } else if found_license && tag.ends_with("name") {
                        in_name = true;
                    }
                }
                Ok(Event::Text(e)) => {
                    if in_name {
                        if let Ok(s) = e.unescape() {
                            license_name = Some(s.to_string());
                            in_name = false;
                            break;
                        }
                    }
                }
                Ok(Event::Eof) => break,
                Err(_) => break,
                _ => {}
            }
            buf.clear();
        }

        if let Some(name) = license_name {
            let norm = normalize_text_block(&name, true);
            return Some(Block {
                source: path.to_string_lossy().to_string(),
                file_path: path.to_string_lossy().to_string(),
                block_type: "metadata_license_field".to_string(),
                start_line: None,
                end_line: None,
                raw_text: name.clone(),
                text: norm.clone(),
                extracted_by: "step1_text_extractor_rust".to_string(),
                repo_root: path
                    .parent()
                    .map(|p| p.to_string_lossy().to_string())
                    .unwrap_or_default(),
                word_count: norm.split_whitespace().count(),
                contains_license_keyword: contains_license_keywords(&norm),
            });
        }
    }
    None
}

fn parse_setup_py(path: &Path) -> Option<Block> {
    if let Ok(txt) = fs::read_to_string(path) {
        let re = Regex::new(r#"license\s*=\s*["']([^"']+)["']"#).unwrap();
        if let Some(cap) = re.captures(&txt) {
            if let Some(m) = cap.get(1) {
                let s = m.as_str().to_string();
                let norm = normalize_text_block(&s, true);
                return Some(Block {
                    source: path.to_string_lossy().to_string(),
                    file_path: path.to_string_lossy().to_string(),
                    block_type: "metadata_license_field".to_string(),
                    start_line: None,
                    end_line: None,
                    raw_text: s.clone(),
                    text: norm.clone(),
                    extracted_by: "step1_text_extractor_rust".to_string(),
                    repo_root: path
                        .parent()
                        .map(|p| p.to_string_lossy().to_string())
                        .unwrap_or_default(),
                    word_count: norm.split_whitespace().count(),
                    contains_license_keyword: contains_license_keywords(&norm),
                });
            }
        }
    }
    None
}

fn extract_metadata_license_blocks(repo_root: &Path) -> Vec<Block> {
    let mut results = Vec::new();

    for entry in WalkDir::new(repo_root)
        .max_depth(6)
        .into_iter()
        .filter_map(Result::ok)
    {
        let p = entry.path().to_path_buf();
        if !p.is_file() {
            continue;
        }
        if let Some(name) = p.file_name().and_then(|n| n.to_str()) {
            match name {
                "package.json" => {
                    if let Some(b) = parse_package_json(&p) {
                        results.push(b);
                    }
                }
                "pyproject.toml" => {
                    if let Some(b) = parse_pyproject_toml(&p) {
                        results.push(b);
                    }
                }
                "Cargo.toml" => {
                    if let Some(b) = parse_cargo_toml(&p) {
                        results.push(b);
                    }
                }
                "pom.xml" => {
                    if let Some(b) = parse_pom_xml(&p) {
                        results.push(b);
                    }
                }
                "setup.py" => {
                    if let Some(b) = parse_setup_py(&p) {
                        results.push(b);
                    }
                }
                _ => {}
            }
        }
    }

    results
}

fn extract_readme_paragraphs(repo_root: &Path) -> Vec<Block> {
    let mut blocks = Vec::new();
    for entry in WalkDir::new(repo_root)
        .max_depth(4)
        .into_iter()
        .filter_map(Result::ok)
    {
        if !entry.file_type().is_file() {
            continue;
        }
        if let Some(name) = entry.file_name().and_then(|n| n.to_str()) {
            if name.to_lowercase().starts_with("readme") {
                if let Ok(txt) = fs::read_to_string(entry.path()) {
                    for para in txt.split("\n\n") {
                        if contains_license_keywords(para) && para.split_whitespace().count() > 8 {
                            let norm = normalize_text_block(para, true);
                            blocks.push(Block {
                                source: entry.path().to_string_lossy().to_string(),
                                file_path: entry.path().to_string_lossy().to_string(),
                                block_type: "readme_paragraph".to_string(),
                                start_line: None,
                                end_line: None,
                                raw_text: para.to_string(),
                                text: norm.clone(),
                                extracted_by: "step1_text_extractor_rust".to_string(),
                                repo_root: repo_root.to_string_lossy().to_string(),
                                word_count: norm.split_whitespace().count(),
                                contains_license_keyword: contains_license_keywords(&norm),
                            })
                        }
                    }
                }
            }
        }
    }
    blocks
}

fn dedupe_blocks(mut blocks: Vec<Block>) -> Vec<Block> {
    let mut seen = HashSet::new();
    let mut out = Vec::new();
    for b in blocks.into_iter() {
        let key = format!("{}|{}", b.block_type, b.text.replace('\n', " ").split_whitespace().collect::<Vec<&str>>().join(" "));
        if !seen.contains(&key) {
            seen.insert(key.clone());
            out.push(b);
        }
    }
    out
}

fn extract_text_blocks_from_repo(repo_root: &Path) -> Vec<Block> {
    let license_files = find_license_files(repo_root);
    let mut blocks = Vec::new();
    blocks.extend(extract_full_license_blocks(license_files, repo_root));
    blocks.extend(extract_header_comment_blocks(repo_root));
    blocks.extend(extract_metadata_license_blocks(repo_root));
    blocks.extend(extract_readme_paragraphs(repo_root));

    let deduped = dedupe_blocks(blocks);
    deduped
}

fn clone_git_to_temp(git_url: &str) -> io::Result<PathBuf> {
    let temp_dir = std::env::temp_dir().join(format!("lic_scan_{}", uuid::Uuid::new_v4()));
    let temp_dir_str = temp_dir.to_string_lossy().to_string();
    fs::create_dir_all(&temp_dir)?;
    let status = std::process::Command::new("git")
        .arg("clone")
        .arg("--depth")
        .arg("1")
        .arg(git_url)
        .arg(&temp_dir_str)
        .status()?;
    if !status.success() {
        fs::remove_dir_all(&temp_dir).ok();
        Err(io::Error::new(
            io::ErrorKind::Other,
            "git clone failed (non-zero exit)",
        ))
    } else {
        Ok(temp_dir)
    }
}

fn main() -> io::Result<()> {
    let args = Args::parse();

    let mut temp_clone: Option<PathBuf> = None;
    let repo_root_path: PathBuf;

    if args.path.starts_with("http://")
        || args.path.starts_with("https://")
        || args.path.starts_with("git@")
    {
        eprintln!("Cloning {} into temp dir...", args.path);
        match clone_git_to_temp(&args.path) {
            Ok(p) => {
                temp_clone = Some(p.clone());
                repo_root_path = p;
            }
            Err(e) => {
                eprintln!("git clone failed: {:?}", e);
                std::process::exit(2);
            }
        }
    } else {
        repo_root_path = PathBuf::from(&args.path);
        if !repo_root_path.exists() {
            eprintln!("Repo path {} not found", args.path);
            std::process::exit(2);
        }
    }

    eprintln!("Extracting license-relevant text blocks from {} ...", repo_root_path.display());
    let mut blocks = extract_text_blocks_from_repo(&repo_root_path);

    // Add metadata fields
    for b in blocks.iter_mut() {
        if b.extracted_by.is_empty() {
            b.extracted_by = "step1_text_extractor_rust".to_string();
        }
        if b.repo_root.is_empty() {
            b.repo_root = repo_root_path.to_string_lossy().to_string();
        }
    }

    if args.max_blocks > 0 && blocks.len() > args.max_blocks {
        blocks.truncate(args.max_blocks);
    }

    // Output
    if args.jsonl {
        let mut out_file = fs::File::create(&args.out)?;
        for b in blocks.iter() {
            let line = serde_json::to_string(b).unwrap();
            use std::io::Write;
            out_file.write_all(line.as_bytes())?;
            out_file.write_all(b"\n")?;
        }
        eprintln!("Wrote {} blocks to {} (jsonl)", blocks.len(), args.out);
    } else {
        let s = serde_json::to_string_pretty(&blocks).unwrap();
        fs::write(&args.out, s)?;
        eprintln!("Wrote {} blocks to {}", blocks.len(), args.out);
    }

    if let Some(tmp) = temp_clone {
        eprintln!("Removing temp clone {}", tmp.display());
        fs::remove_dir_all(tmp).ok();
    }

    Ok(())
}
