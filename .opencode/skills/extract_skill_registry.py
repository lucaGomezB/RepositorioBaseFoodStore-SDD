import os
import re
import json
from pathlib import Path


def parse_front_matter(text):
    match = re.match(r'^---\s*\n(.*?)(?=\n---\s*\n)', text, re.S)
    if not match:
        return {}
    content = match.group(1)
    result = {}
    lines = content.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith('name:'):
            result['name'] = stripped.split(':', 1)[1].strip()
        elif stripped.startswith('description:'):
            value = stripped.split(':', 1)[1].strip()
            if value in ('>', '|'):
                i += 1
                description_lines = []
                while i < len(lines) and (lines[i].startswith('  ') or lines[i].startswith('\t')):
                    description_lines.append(lines[i].strip())
                    i += 1
                result['description'] = ' '.join(description_lines).strip()
                continue
            else:
                result['description'] = value
        elif stripped.lower().startswith('trigger:'):
            result['trigger'] = stripped.split(':', 1)[1].strip()
        i += 1
    return result


def extract_trigger(description, full_text, front_end):
    if not description:
        return ''
    m = re.search(r'Trigger:\s*(.*)', description, re.I)
    if m:
        return m.group(1).strip()
    for line in full_text[front_end:].splitlines():
        if line.strip().lower().startswith('trigger:'):
            return line.split(':', 1)[1].strip()
    return ''


def clean_text(value):
    return ' '.join(value.split()).strip()


entries = []
root = Path('.')
for d in sorted(os.listdir(root)):
    if not (root / d).is_dir() or d == '_shared':
        continue
    md_path = root / d / 'SKILL.md'
    if not md_path.exists():
        continue
    text = md_path.read_text(encoding='utf-8')
    meta = parse_front_matter(text)
    desc = clean_text(meta.get('description', ''))
    trigger = clean_text(meta.get('trigger', ''))
    front_end = 0
    m = re.search(r'^---\s*\n.*?\n---\s*\n', text, re.S)
    if m:
        front_end = m.end()
    if not trigger:
        trigger = clean_text(extract_trigger(desc, text, front_end))
        if 'Trigger:' in desc:
            desc = clean_text(re.sub(r'Trigger:\s*.*', '', desc, flags=re.I))
    if not trigger:
        fallback = {
            'code-review-excellence': 'When reviewing pull requests or establishing review standards.',
            'fastapi-templates': '.py / fastapi-python / backend API scaffolding.',
            'find-skills': 'When the user asks to discover or install a skill.',
            'openspec-apply-change': 'When implementing an OpenSpec change.',
            'openspec-archive-change': 'When archiving a completed OpenSpec change.',
            'openspec-explore': 'When the user wants to explore ideas or clarify requirements before a change.',
            'openspec-propose': 'When proposing a new OpenSpec change.',
            'systematic-debugging': 'When diagnosing a bug, test failure, or unexpected behavior.',
            'tailwind-design-system': 'When building UIs with Tailwind CSS.',
            'test-driven-development': 'When implementing features or bug fixes with TDD.',
        }
        trigger = fallback.get(d, '')
    entries.append({
        'name': d,
        'trigger': trigger,
        'description': desc,
    })

with open('registry.json', 'w', encoding='utf-8') as f:
    json.dump(entries, f, ensure_ascii=False, indent=2)

print(f'Written registry.json with {len(entries)} entries')
