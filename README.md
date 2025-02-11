# Anwa Solutions Backend

This repository contains the backend for the comprehensive restaurant management system **Anwa Solutions**, developed using **Django Rest Framework**. The system handles functionalities such as menu management, order processing, automated billing, and inventory control with real-time integration via APIs.

## 🚀 Main Features

- **Menu Management**: Intuitive product, category, and pricing management.
- **Order Processing**: Real-time order handling with WhatsApp integration.
- **Automated Billing**: Efficiently generate detailed invoices, including tips.
- **Inventory Control**: Keep inventory updated and manageable.

## 🛠️ Technologies Used
- **React**: Frontend framework
- **Python**: Core language for backend development.
- **Django Rest Framework**: Framework for building APIs.
- **PostgreSQL**: Relational database.
- **Git**: Version control.

## 📦 Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/anwa-solutions-backend.git
   cd anwa-solutions-backend
   ```

2. Set up a virtual environment:
   ```bash
   python -m venv env
   source env/bin/activate  # For Linux/Mac
   env\Scripts\activate     # For Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure the `.env` file with your environment variables:
   - Set up database credentials.
   - Add WhatsApp API credentials and other required services.

5. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. Start the development server:
   ```bash
   python manage.py runserver
   ```

## 📖 Project Structure

- **`/anwa_solutions/`**: Main application.
- **`/orders/`**: Order management module.
- **`/billing/`**: Billing module.
- **`/inventory/`**: Inventory control module.
- **`/menu/`**: Menu management module.
- **`/docs/`**: Technical and functional documentation.

## 🌐 Key API Endpoints


## 🗒️ System Requirements

- **Python 3.10+**
- **PostgreSQL 13+**
- **Docker** (optional, for deployment)

## 📌 Notes

- **Internet Connection**: Required for real-time integrations.
- **Device Compatibility**: Ensure compatibility with WhatsApp and mobile browsers.
- **Updates**: Regular updates of the system and dependencies are essential for optimal performance.

## 🤝 Contribution Guidelines

We welcome contributions to the project! To ensure consistency and quality, please follow these steps:

1. Fork the repository.
2. Create a new branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Use **Conventional Commits** for commit messages:
   ```
   feat: Add new API endpoint for orders
   fix: Correct menu validation error
   docs: Update API documentation
   ```
   Refer to [Conventional Commits](https://www.conventionalcommits.org/) for more details.

4. Push your branch and create a Pull Request (PR):
   ```bash
   git push origin feature/your-feature-name
   ```
5. Submit a detailed PR describing your changes and their impact.
6. Ensure your code passes all tests and follows the project’s style guidelines.

## 📞 Support

For questions or support, contact the team:

---

Feel free to suggest improvements or report issues in the repository. Let's build something amazing together!

