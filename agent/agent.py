#!/usr/bin/env python3
"""
Docker TUI Agent
Runs on local machine to sync Docker data with remote backend.
"""

import docker
import requests
import time
import json
import logging
import sys
from typing import Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DockerAgent:
    """Agent to sync local Docker data with backend."""

    def __init__(self, backend_url: str, agent_token: str, sync_interval: int = 5):
        """
        Initialize agent.

        Args:
            backend_url: Backend API URL (e.g., https://your-backend.com)
            agent_token: Agent authentication token
            sync_interval: How often to sync data (seconds)
        """
        self.backend_url = backend_url.rstrip('/')
        self.agent_token = agent_token
        self.sync_interval = sync_interval
        self.docker_client = None
        self.running = True

        # Initialize Docker client
        try:
            self.docker_client = docker.from_env()
            logger.info("✓ Connected to Docker")
        except Exception as e:
            logger.error(f"✗ Failed to connect to Docker: {e}")
            logger.error("Make sure Docker is running and accessible.")
            sys.exit(1)

    def get_headers(self):
        """Get authorization headers."""
        return {
            "Authorization": f"Bearer {self.agent_token}",
            "Content-Type": "application/json"
        }

    def fetch_containers(self):
        """Fetch container data from local Docker."""
        try:
            containers = self.docker_client.containers.list(all=True)
            container_data = []

            for container in containers:
                # Get port mappings
                ports = container.attrs.get("NetworkSettings", {}).get("Ports", {}) or {}

                # Get image name
                image_tags = container.image.tags if container.image.tags else [container.image.short_id]
                image_name = image_tags[0] if image_tags else "unknown"

                container_info = {
                    "id": container.id,
                    "short_id": container.short_id,
                    "name": container.name,
                    "image": image_name,
                    "status": container.status,
                    "state": container.attrs.get("State", {}).get("Status", "unknown"),
                    "ports": ports,
                    "created": container.attrs.get("Created", "")[:19],
                    "cpu_percent": 0.0,
                    "memory_usage": "0B",
                    "memory_percent": 0.0
                }

                # Try to get stats (non-blocking)
                try:
                    if container.status == "running":
                        stats = container.stats(stream=False)

                        # Calculate CPU percentage
                        cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - \
                                   stats["precpu_stats"]["cpu_usage"]["total_usage"]
                        system_delta = stats["cpu_stats"]["system_cpu_usage"] - \
                                      stats["precpu_stats"]["system_cpu_usage"]
                        cpu_count = stats["cpu_stats"]["online_cpus"]

                        if system_delta > 0:
                            cpu_percent = (cpu_delta / system_delta) * cpu_count * 100.0
                            container_info["cpu_percent"] = round(cpu_percent, 2)

                        # Calculate memory usage
                        mem_usage = stats["memory_stats"]["usage"]
                        mem_limit = stats["memory_stats"]["limit"]
                        mem_percent = (mem_usage / mem_limit) * 100.0

                        container_info["memory_usage"] = self._format_bytes(mem_usage)
                        container_info["memory_percent"] = round(mem_percent, 2)
                except Exception as e:
                    logger.debug(f"Could not get stats for {container.name}: {e}")

                container_data.append(container_info)

            return container_data

        except Exception as e:
            logger.error(f"Error fetching containers: {e}")
            return []

    def fetch_images(self):
        """Fetch image data from local Docker."""
        try:
            images = self.docker_client.images.list()
            image_data = []

            for image in images:
                image_info = {
                    "id": image.id,
                    "short_id": image.short_id,
                    "tags": image.tags,
                    "size": self._format_bytes(image.attrs.get("Size", 0)),
                    "created": image.attrs.get("Created", "")[:19]
                }
                image_data.append(image_info)

            return image_data

        except Exception as e:
            logger.error(f"Error fetching images: {e}")
            return []

    def _format_bytes(self, bytes_val):
        """Format bytes to human readable string."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_val < 1024.0:
                return f"{bytes_val:.1f}{unit}"
            bytes_val /= 1024.0
        return f"{bytes_val:.1f}PB"

    def sync_data(self):
        """Sync local Docker data to backend."""
        try:
            containers = self.fetch_containers()
            images = self.fetch_images()

            data = {
                "containers": containers,
                "images": images
            }

            response = requests.post(
                f"{self.backend_url}/api/agent/sync",
                headers=self.get_headers(),
                json=data,
                timeout=10
            )

            if response.status_code == 200:
                logger.info(f"✓ Synced: {len(containers)} containers, {len(images)} images")
                return True
            else:
                logger.error(f"✗ Sync failed: {response.status_code} - {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Network error during sync: {e}")
            return False
        except Exception as e:
            logger.error(f"✗ Error during sync: {e}")
            return False

    def fetch_actions(self):
        """Fetch pending actions from backend."""
        try:
            response = requests.get(
                f"{self.backend_url}/api/agent/actions",
                headers=self.get_headers(),
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("actions", [])
            else:
                logger.error(f"✗ Failed to fetch actions: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"✗ Error fetching actions: {e}")
            return []

    def execute_action(self, action):
        """Execute a single action."""
        action_id = action["id"]
        action_type = action["action_type"]
        target_type = action["target_type"]
        target_id = action["target_id"]

        logger.info(f"→ Executing: {action_type} {target_type} {target_id}")

        success = False
        message = ""

        try:
            if target_type == "container":
                success, message = self._execute_container_action(action_type, target_id)
            elif target_type == "image":
                success, message = self._execute_image_action(action_type, target_id)
            else:
                message = f"Unknown target type: {target_type}"

        except Exception as e:
            message = f"Error: {str(e)}"
            logger.error(f"✗ Action failed: {message}")

        # Report result to backend
        self.complete_action(action_id, success, message)

        if success:
            logger.info(f"✓ Action completed: {message}")
        else:
            logger.error(f"✗ Action failed: {message}")

        return success

    def _execute_container_action(self, action_type, container_id):
        """Execute container action."""
        try:
            container = self.docker_client.containers.get(container_id)

            if action_type == "start":
                container.start()
                return True, "Container started"

            elif action_type == "stop":
                container.stop()
                return True, "Container stopped"

            elif action_type == "restart":
                container.restart()
                return True, "Container restarted"

            elif action_type == "delete":
                container.remove(force=False)
                return True, "Container deleted"

            elif action_type == "delete_force":
                container.remove(force=True)
                return True, "Container force deleted"

            else:
                return False, f"Unknown action: {action_type}"

        except docker.errors.NotFound:
            return False, "Container not found"
        except Exception as e:
            return False, str(e)

    def _execute_image_action(self, action_type, image_id):
        """Execute image action."""
        try:
            if action_type == "pull":
                # image_id is actually the image name for pull
                logger.info(f"Pulling image: {image_id}")
                self.docker_client.images.pull(image_id)
                return True, f"Image {image_id} pulled"

            elif action_type == "delete":
                image = self.docker_client.images.get(image_id)
                self.docker_client.images.remove(image.id, force=False)
                return True, "Image deleted"

            elif action_type == "delete_force":
                image = self.docker_client.images.get(image_id)
                self.docker_client.images.remove(image.id, force=True)
                return True, "Image force deleted"

            else:
                return False, f"Unknown action: {action_type}"

        except docker.errors.ImageNotFound:
            return False, "Image not found"
        except docker.errors.NotFound:
            return False, "Image not found"
        except Exception as e:
            return False, str(e)

    def complete_action(self, action_id, success, message):
        """Report action completion to backend."""
        try:
            response = requests.post(
                f"{self.backend_url}/api/agent/actions/{action_id}/complete",
                headers=self.get_headers(),
                json={"success": success, "message": message},
                timeout=10
            )

            if response.status_code != 200:
                logger.error(f"Failed to report action completion: {response.status_code}")

        except Exception as e:
            logger.error(f"Error reporting action completion: {e}")

    def run(self):
        """Main agent loop."""
        logger.info("=" * 60)
        logger.info("Docker TUI Agent Started")
        logger.info(f"Backend: {self.backend_url}")
        logger.info(f"Sync Interval: {self.sync_interval}s")
        logger.info("=" * 60)

        last_sync = 0

        try:
            while self.running:
                current_time = time.time()

                # Sync data periodically
                if current_time - last_sync >= self.sync_interval:
                    self.sync_data()
                    last_sync = current_time

                # Check for pending actions
                actions = self.fetch_actions()
                for action in actions:
                    self.execute_action(action)
                    # Sync immediately after action to update status
                    self.sync_data()
                    last_sync = time.time()

                # Sleep briefly
                time.sleep(1)

        except KeyboardInterrupt:
            logger.info("\n✓ Agent stopped by user")
        except Exception as e:
            logger.error(f"✗ Agent error: {e}")
            raise

    def stop(self):
        """Stop the agent."""
        self.running = False


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Docker TUI Agent')
    parser.add_argument('--backend', required=True, help='Backend URL (e.g., https://your-backend.com)')
    parser.add_argument('--token', required=True, help='Agent authentication token')
    parser.add_argument('--interval', type=int, default=5, help='Sync interval in seconds (default: 5)')

    args = parser.parse_args()

    agent = DockerAgent(
        backend_url=args.backend,
        agent_token=args.token,
        sync_interval=args.interval
    )

    agent.run()


if __name__ == "__main__":
    main()
