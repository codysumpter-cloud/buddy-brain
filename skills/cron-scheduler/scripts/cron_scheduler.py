#!/usr/bin/env python3
"""
Cron Scheduler for bmo-stack
Handles scheduling, validation, and execution of routine jobs
"""

import os
import sys
import json
import argparse
import subprocess
from datetime import datetime
from croniter import croniter
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Paths
BMO_STACK_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOBS_FILE = os.path.join(BMO_STACK_ROOT, 'logs', 'cron', 'jobs.json')
LOGS_DIR = os.path.join(BMO_STACK_ROOT, 'logs', 'cron')

def ensure_directories():
    """Ensure required directories exist"""
    os.makedirs(LOGS_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(JOBS_FILE), exist_ok=True)

def load_jobs():
    """Load scheduled jobs from JSON file"""
    if not os.path.exists(JOBS_FILE):
        return []
    try:
        with open(JOBS_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_jobs(jobs):
    """Save jobs to JSON file"""
    with open(JOBS_FILE, 'w') as f:
        json.dump(jobs, f, indent=2)

def validate_cron_expression(expression):
    """Validate a cron expression"""
    try:
        croniter(expression)
        return True
    except Exception:
        return False

def parse_cron_time(expression):
    """Parse cron expression to get next run time"""
    try:
        base = croniter(expression, datetime.now())
        return base.get_next(datetime)
    except Exception:
        return None

def check_schedule_collision(new_job):
    """Check if new job collides with existing jobs (5-minute rule)"""
    existing_jobs = load_jobs()
    new_cron = croniter(new_job['schedule'], datetime.now())
    
    # Get the next 5-minute slot for the new job
    new_slot = new_cron.get_next(datetime)
    new_slot = new_slot.replace(second=0, microsecond=0)
    # Round to nearest 5-minute interval
    minute = new_slot.minute
    remainder = minute % 5
    if remainder != 0:
        new_slot = new_slot.replace(minute=new_slot.minute - remainder)
    
    # Check against existing jobs
    for job in existing_jobs:
        if not validate_cron_expression(job['schedule']):
            continue
        try:
            job_cron = croniter(job['schedule'], datetime.now())
            job_slot = job_cron.get_next(datetime)
            job_slot = job_slot.replace(second=0, microsecond=0)
            minute = job_slot.minute
            remainder = minute % 5
            if remainder != 0:
                job_slot = job_slot.replace(minute=job_slot.minute - remainder)
            
            # If slots match, there's a collision
            if job_slot == new_slot:
                return True, job_slot
        except Exception:
            continue
    
    return False, None

def suggest_next_slot(base_time, offset_minutes=5):
    """Suggest the next available slot"""
    # This is a simplified version - in practice would check against all jobs
    suggested = base_time.replace(second=0, microsecond=0)
    return suggested

def doctor():
    """Check the health of the cron scheduler"""
    print("🔍 Cron Scheduler Health Check")
    print("=" * 40)
    
    ensure_directories()
    jobs = load_jobs()
    
    print(f"📋 Total scheduled jobs: {len(jobs)}")
    
    valid_jobs = 0
    invalid_jobs = 0
    collisions = []
    
    for i, job in enumerate(jobs):
        print(f"\nJob {i+1}: {job.get('name', 'unnamed')}")
        print(f"  Schedule: {job.get('schedule', 'N/A')}")
        print(f"  Skill: {job.get('skill', 'N/A')}")
        
        # Validate cron expression
        if validate_cron_expression(job.get('schedule', '')):
            print(f"  ✅ Valid cron expression")
            valid_jobs += 1
            
            # Check for collisions
            is_collide, collision_time = check_schedule_collision(job)
            if is_collide:
                print(f"  ⚠️  Collision detected at {collision_time.strftime('%Y-%m-%d %H:%M')}")
                collisions.append((job.get('name', 'unnamed'), collision_time))
            else:
                next_run = parse_cron_time(job['schedule'])
                if next_run:
                    print(f"  ⏰ Next run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"  ❌ Invalid cron expression")
            invalid_jobs += 1
    
    if collisions:
        print(f"\n⚠️  Found {len(collisions)} schedule collision(s):")
        for job_name, time in collisions:
            print(f"   - {job_name} at {time.strftime('%Y-%m-%d %H:%M')}")
        print("   Suggestion: Reschedule one of the conflicting jobs")
    else:
        print(f"\n✅ No schedule collisions detected")
    
    if invalid_jobs == 0 and len(collisions) == 0:
        print(f"\n🎉 All checks passed!")
        return True
    else:
        print(f"\n💥 Health check failed")
        return False

def schedule_job(name, schedule, skill, timeout=300):
    """Schedule a new cron job"""
    print(f"📝 Scheduling job: {name}")
    
    ensure_directories()
    
    # Validate inputs
    if not name or not schedule or not skill:
        print("❌ Error: name, schedule, and skill are required")
        return False
    
    if not validate_cron_expression(schedule):
        print(f"❌ Error: Invalid cron expression '{schedule}'")
        return False
    
    # Check if skill exists
    skill_path = os.path.join(BMO_STACK_ROOT, 'skills', skill)
    if not os.path.exists(skill_path):
        print(f"⚠️  Warning: Skill '{skill}' not found at {skill_path}")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            return False
    
    # Check for collisions
    new_job = {
        'name': name,
        'schedule': schedule,
        'skill': skill,
        'timeout': timeout,
        'created_at': datetime.now().isoformat()
    }
    
    is_collide, collision_time = check_schedule_collision(new_job)
    if is_collide:
        print(f"❌ Error: Schedule collides with existing job at {collision_time.strftime('%Y-%m-%d %H:%M')}")
        print("   Use a different cron expression to avoid collisions")
        return False
    
    # Add job
    jobs = load_jobs()
    jobs.append(new_job)
    save_jobs(jobs)
    
    next_run = parse_cron_time(schedule)
    print(f"✅ Job '{name}' scheduled successfully")
    if next_run:
        print(f"   Next run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
    
    return True

def list_jobs():
    """List all scheduled jobs"""
    ensure_directories()
    jobs = load_jobs()
    
    if not jobs:
        print("📭 No scheduled jobs")
        return
    
    print(f"📋 Scheduled Jobs ({len(jobs)} total)")
    print("=" * 60)
    
    for i, job in enumerate(jobs, 1):
        print(f"{i}. {job['name']}")
        print(f"   Schedule: {job['schedule']}")
        print(f"   Skill: {job['skill']}")
        print(f"   Timeout: {job.get('timeout', 300)}s")
        
        if validate_cron_expression(job['schedule']):
            next_run = parse_cron_time(job['schedule'])
            if next_run:
                print(f"   Next run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Check quiet hours (simplified)
            now = datetime.now()
            hour = now.hour
            if 22 <= hour or hour < 8:  # 10 PM to 8 AM
                print(f"   Status: ⏳ Quiet hours (will run if user is awake)")
            else:
                print(f"   Status: 🟢 Active hours")
        else:
            print(f"   Status: ❌ Invalid schedule")
        print()

def run_job(name):
    """Run a specific job immediately"""
    ensure_directories()
    jobs = load_jobs()
    
    job = None
    for j in jobs:
        if j['name'] == name:
            job = j
            break
    
    if not job:
        print(f"❌ Error: Job '{name}' not found")
        return False
    
    skill = job['skill']
    timeout = job.get('timeout, 300')
    
    print(f"🚀 Running job: {name}")
    print(f"   Skill: {skill}")
    print(f"   Timeout: {timeout}s")
    
    # Execute the skill
    skill_path = os.path.join(BMO_STACK_ROOT, 'skills', skill)
    if not os.path.exists(skill_path):
        print(f"❌ Error: Skill '{skill}' not found")
        return False
    
    # Create log entry
    log_dir = os.path.join(LOGS_DIR, name)
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    log_file = os.path.join(log_dir, f'{timestamp}.md')
    
    # Run the skill via hermes command (simplified)
    # In practice, this would invoke the skill through the proper channel
    cmd = [
        'hermes',
        '-c',
        f'cd {BMO_STACK_ROOT} && echo "Running skill {skill} for job {name}" >> {log_file}'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        with open(log_file, 'w') as f:
            f.write(f"# Job Execution Log: {name}\n\n")
            f.write(f"**Started**: {datetime.now().isoformat()}\n")
            f.write(f"**Skill**: {skill}\n")
            f.write(f"**Timeout**: {timeout}s\n\n")
            f.write("## Output\n\n```\n")
            f.write(result.stdout)
            if result.stderr:
                f.write("\nSTDERR:\n")
                f.write(result.stderr)
            f.write("\n```\n\n")
            f.write(f"**Exit Code**: {result.returncode}\n")
        
        if result.returncode == 0:
            print(f"✅ Job completed successfully")
            print(f"   Log saved to: {log_file}")
            return True
        else:
            print(f"❌ Job failed with exit code {result.returncode}")
            print(f"   Log saved to: {log_file}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"❌ Job timed out after {timeout} seconds")
        return False
    except Exception as e:
        print(f"❌ Error running job: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Cron Scheduler for bmo-stack')
    parser.add_argument('action', choices=['doctor', 'schedule', 'list', 'run'],
                       help='Action to perform')
    parser.add_argument('--name', help='Job name')
    parser.add_argument('--schedule', help='Cron expression (e.g., "0 9 * * *")')
    parser.add_argument('--skill', help='Skill to run')
    parser.add_argument('--timeout', type=int, default=300, help='Timeout in seconds')
    
    args = parser.parse_args()
    
    if args.action == 'doctor':
        success = doctor()
        sys.exit(0 if success else 1)
    elif args.action == 'schedule':
        if not all([args.name, args.schedule, args.skill]):
            print("❌ Error: --name, --schedule, and --skill are required for schedule action")
            sys.exit(1)
        success = schedule_job(args.name, args.schedule, args.skill, args.timeout)
        sys.exit(0 if success else 1)
    elif args.action == 'list':
        list_jobs()
    elif args.action == 'run':
        if not args.name:
            print("❌ Error: --name is required for run action")
            sys.exit(1)
        success = run_job(args.name)
        sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()