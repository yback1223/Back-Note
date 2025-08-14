#!/bin/bash

# Back Note Application Startup Script
# This script helps you start the application in different environments

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    mkdir -p data logs ssl
    # Ensure proper permissions for data directory
    chmod 755 data logs ssl
    print_success "Directories created"
}

# Function to check database persistence
check_database_persistence() {
    if [ -f "data/my_app_database.db" ]; then
        print_success "Database file found in data directory"
        print_status "Database size: $(du -h data/my_app_database.db | cut -f1)"
    else
        print_warning "No existing database found. A new database will be created."
    fi
}

# Function to generate self-signed SSL certificate for development
generate_ssl_cert() {
    if [ ! -f "ssl/cert.pem" ] || [ ! -f "ssl/key.pem" ]; then
        print_status "Generating self-signed SSL certificate for development..."
        mkdir -p ssl
        openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
        print_success "SSL certificate generated"
    else
        print_status "SSL certificate already exists"
    fi
}

# Function to start development environment
start_dev() {
    print_status "Starting development environment..."
    check_docker
    create_directories
    check_database_persistence
    
    docker-compose up --build -d
    print_success "Development environment started"
    print_status "Application is available at: http://localhost:8501"
    print_status "Database is persisted in: ./data/my_app_database.db"
}

# Function to start production environment
start_prod() {
    print_status "Starting production environment..."
    check_docker
    create_directories
    check_database_persistence
    generate_ssl_cert
    
    docker-compose -f docker-compose.prod.yml up --build -d
    print_success "Production environment started"
    print_status "Application is available at: https://localhost"
    print_status "Database is persisted in: ./data/my_app_database.db"
}

# Function to stop the application
stop_app() {
    print_status "Stopping application..."
    docker-compose down
    docker-compose -f docker-compose.prod.yml down 2>/dev/null || true
    print_success "Application stopped"
    print_status "Database is preserved in: ./data/my_app_database.db"
}

# Function to view logs
view_logs() {
    print_status "Showing application logs..."
    docker-compose logs -f
}

# Function to backup database
backup_database() {
    if [ -f "data/my_app_database.db" ]; then
        backup_file="data/backup_$(date +%Y%m%d_%H%M%S).db"
        cp data/my_app_database.db "$backup_file"
        print_success "Database backed up to: $backup_file"
    else
        print_warning "No database file found to backup"
    fi
}

# Function to clean up
cleanup() {
    print_warning "This will remove all containers, images, and volumes. Are you sure? (y/N)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_status "Cleaning up..."
        docker-compose down -v --rmi all
        docker-compose -f docker-compose.prod.yml down -v --rmi all 2>/dev/null || true
        docker system prune -f
        print_success "Cleanup completed"
        print_warning "Note: Database file in ./data/ is preserved"
    else
        print_status "Cleanup cancelled"
    fi
}

# Function to show status
show_status() {
    print_status "Application status:"
    docker-compose ps
    echo ""
    print_status "Container logs:"
    docker-compose logs --tail=10
    echo ""
    check_database_persistence
}

# Function to show help
show_help() {
    echo "Back Note Application Management Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  dev     Start development environment"
    echo "  prod    Start production environment"
    echo "  stop    Stop the application"
    echo "  logs    View application logs"
    echo "  status  Show application status"
    echo "  backup  Backup the database"
    echo "  clean   Clean up all containers and images"
    echo "  help    Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 dev     # Start development environment"
    echo "  $0 prod    # Start production environment"
    echo "  $0 stop    # Stop the application"
    echo ""
    echo "Database Persistence:"
    echo "  - Database is stored in: ./data/my_app_database.db"
    echo "  - Data persists between container restarts"
    echo "  - Use 'backup' command to create database backups"
}

# Main script logic
case "${1:-help}" in
    dev)
        start_dev
        ;;
    prod)
        start_prod
        ;;
    stop)
        stop_app
        ;;
    logs)
        view_logs
        ;;
    status)
        show_status
        ;;
    backup)
        backup_database
        ;;
    clean)
        cleanup
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
