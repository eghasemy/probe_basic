#!/usr/bin/env python
"""
Phase 10 Version Management and Changelog System
Automatic versioning and changelog generation for probe_basic
"""

import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    from probe_basic.logging_config import get_main_logger
    logger = get_main_logger()
except ImportError:
    import logging
    logger = logging.getLogger('version_manager')

class VersionManager:
    """Manages versioning and changelog for probe_basic"""
    
    def __init__(self, repo_path: Optional[Path] = None):
        self.repo_path = repo_path or Path.cwd()
        self.version_file = self.repo_path / 'VERSION'
        self.changelog_file = self.repo_path / 'CHANGELOG.md'
        
    def get_current_version(self) -> str:
        """Get current version from git tags or VERSION file"""
        try:
            # Try to get version from git tags
            result = subprocess.run(
                ['git', 'describe', '--tags', '--always'],
                capture_output=True, text=True, cwd=self.repo_path
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                logger.debug(f"Version from git: {version}")
                return version
        except Exception as e:
            logger.debug(f"Could not get version from git: {e}")
        
        # Fallback to VERSION file
        if self.version_file.exists():
            with open(self.version_file, 'r') as f:
                version = f.read().strip()
                logger.debug(f"Version from file: {version}")
                return version
        
        # Default version
        default_version = "0.1.0-dev"
        logger.debug(f"Using default version: {default_version}")
        return default_version
    
    def bump_version(self, part: str = 'patch') -> str:
        """
        Bump version number
        
        Args:
            part: 'major', 'minor', or 'patch'
            
        Returns:
            New version string
        """
        current = self.get_current_version()
        
        # Extract version parts (handle various formats)
        version_match = re.match(r'v?(\d+)\.(\d+)\.(\d+)', current)
        if not version_match:
            logger.warning(f"Could not parse version {current}, using 0.1.0")
            major, minor, patch = 0, 1, 0
        else:
            major, minor, patch = map(int, version_match.groups())
        
        # Bump appropriate part
        if part == 'major':
            major += 1
            minor = 0
            patch = 0
        elif part == 'minor':
            minor += 1
            patch = 0
        elif part == 'patch':
            patch += 1
        else:
            raise ValueError(f"Invalid version part: {part}")
        
        new_version = f"{major}.{minor}.{patch}"
        
        # Write to VERSION file
        with open(self.version_file, 'w') as f:
            f.write(new_version)
        
        logger.info(f"Version bumped from {current} to {new_version}")
        return new_version
    
    def get_git_commits_since_tag(self, tag: Optional[str] = None) -> List[Dict[str, str]]:
        """Get git commits since specified tag or last tag"""
        try:
            if tag is None:
                # Get last tag
                result = subprocess.run(
                    ['git', 'describe', '--tags', '--abbrev=0'],
                    capture_output=True, text=True, cwd=self.repo_path
                )
                if result.returncode == 0:
                    tag = result.stdout.strip()
                else:
                    tag = None
            
            # Get commits since tag
            if tag:
                cmd = ['git', 'log', f'{tag}..HEAD', '--oneline', '--pretty=format:%h|%s|%an|%ad']
            else:
                cmd = ['git', 'log', '--oneline', '--pretty=format:%h|%s|%an|%ad', '--max-count=50']
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.repo_path)
            
            if result.returncode != 0:
                logger.warning("Could not get git commits")
                return []
            
            commits = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('|', 3)
                    if len(parts) == 4:
                        commits.append({
                            'hash': parts[0],
                            'message': parts[1],
                            'author': parts[2],
                            'date': parts[3]
                        })
            
            return commits
            
        except Exception as e:
            logger.error(f"Error getting git commits: {e}")
            return []
    
    def categorize_commits(self, commits: List[Dict[str, str]]) -> Dict[str, List[Dict[str, str]]]:
        """Categorize commits by type"""
        categories = {
            'Features': [],
            'Bug Fixes': [],
            'Improvements': [],
            'Documentation': [],
            'Tests': [],
            'Build/CI': [],
            'Other': []
        }
        
        for commit in commits:
            message = commit['message'].lower()
            
            if any(keyword in message for keyword in ['feat:', 'feature:', 'add:', 'implement']):
                categories['Features'].append(commit)
            elif any(keyword in message for keyword in ['fix:', 'bug:', 'resolve']):
                categories['Bug Fixes'].append(commit)
            elif any(keyword in message for keyword in ['improve:', 'enhance:', 'update:', 'refactor']):
                categories['Improvements'].append(commit)
            elif any(keyword in message for keyword in ['doc:', 'docs:', 'readme']):
                categories['Documentation'].append(commit)
            elif any(keyword in message for keyword in ['test:', 'tests:', 'pytest']):
                categories['Tests'].append(commit)
            elif any(keyword in message for keyword in ['build:', 'ci:', 'deploy']):
                categories['Build/CI'].append(commit)
            else:
                categories['Other'].append(commit)
        
        return categories
    
    def generate_changelog_entry(self, version: str, commits: List[Dict[str, str]]) -> str:
        """Generate changelog entry for version"""
        date = datetime.now().strftime('%Y-%m-%d')
        
        entry = f"\n## [{version}] - {date}\n\n"
        
        categories = self.categorize_commits(commits)
        
        for category, category_commits in categories.items():
            if category_commits:
                entry += f"### {category}\n\n"
                for commit in category_commits:
                    message = commit['message']
                    # Clean up commit message
                    if ':' in message:
                        message = message.split(':', 1)[1].strip()
                    message = message.capitalize()
                    entry += f"- {message} ({commit['hash']})\n"
                entry += "\n"
        
        return entry
    
    def update_changelog(self, version: str, commits: List[Dict[str, str]]):
        """Update changelog with new version"""
        entry = self.generate_changelog_entry(version, commits)
        
        if self.changelog_file.exists():
            with open(self.changelog_file, 'r') as f:
                existing = f.read()
            
            # Insert new entry after title
            lines = existing.split('\n')
            title_index = -1
            for i, line in enumerate(lines):
                if line.startswith('#') and 'changelog' in line.lower():
                    title_index = i
                    break
            
            if title_index >= 0:
                # Insert after title and description
                insert_index = title_index + 1
                while insert_index < len(lines) and not lines[insert_index].startswith('##'):
                    insert_index += 1
                
                lines.insert(insert_index, entry)
                content = '\n'.join(lines)
            else:
                content = existing + entry
        else:
            # Create new changelog
            content = f"# Probe Basic Changelog\n\nAll notable changes to this project will be documented in this file.\n{entry}"
        
        with open(self.changelog_file, 'w') as f:
            f.write(content)
        
        logger.info(f"Updated changelog with version {version}")
    
    def create_release(self, part: str = 'patch', message: Optional[str] = None) -> Tuple[str, str]:
        """
        Create a new release with version bump and changelog update
        
        Args:
            part: Version part to bump
            message: Optional release message
            
        Returns:
            Tuple of (new_version, changelog_entry)
        """
        # Get commits since last release
        commits = self.get_git_commits_since_tag()
        
        if not commits:
            logger.warning("No commits found since last release")
            return self.get_current_version(), ""
        
        # Bump version
        new_version = self.bump_version(part)
        
        # Update changelog
        self.update_changelog(new_version, commits)
        
        # Generate release notes
        release_notes = self.generate_changelog_entry(new_version, commits)
        
        logger.info(f"Created release {new_version} with {len(commits)} commits")
        
        return new_version, release_notes
    
    def get_release_info(self) -> Dict[str, str]:
        """Get current release information"""
        return {
            'version': self.get_current_version(),
            'date': datetime.now().isoformat(),
            'commits_count': str(len(self.get_git_commits_since_tag())),
            'changelog_exists': str(self.changelog_file.exists())
        }

def main():
    """Command line interface for version management"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Probe Basic Version Manager')
    parser.add_argument('action', choices=['bump', 'info', 'changelog'], 
                       help='Action to perform')
    parser.add_argument('--part', choices=['major', 'minor', 'patch'], 
                       default='patch', help='Version part to bump')
    parser.add_argument('--message', help='Release message')
    
    args = parser.parse_args()
    
    vm = VersionManager()
    
    if args.action == 'bump':
        version, notes = vm.create_release(args.part, args.message)
        print(f"Released version: {version}")
        print("Release notes:")
        print(notes)
    elif args.action == 'info':
        info = vm.get_release_info()
        for key, value in info.items():
            print(f"{key}: {value}")
    elif args.action == 'changelog':
        commits = vm.get_git_commits_since_tag()
        if commits:
            entry = vm.generate_changelog_entry("UNRELEASED", commits)
            print("Upcoming changelog entry:")
            print(entry)
        else:
            print("No unreleased commits found")

if __name__ == '__main__':
    main()