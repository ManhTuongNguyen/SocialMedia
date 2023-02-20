## About The Project
Name: Social Media

Project build with [Django Framework](https://www.djangoproject.com/), [Tailwind CSS](https://tailwindcss.com/)

## Getting Started
To get a local copy up and running follow these simple example steps.
### How to run
1. Clone the repo
   ```sh
   git clone https://github.com/ManhTuongNguyen/SocialMedia.git
   ```
2. Move to the project
   ```
   cd SocialMedia
   ```
3. Install enviroment for this project
   ```sh
   python -m venv env
   ```
4. Active enviroment
   ```sh
   .\env\Scripts\activate
   ```
5. Install module from requirements.txt
   ```sh
   pip install -r requirements.txt
   ```
6. Migrate models
   ```sh
   py manage.py makemigrations
   py manage.py migrate
   ```
7. Run project
    ```
    py manage.py runserver
    ```

### To use function send email
1. Go to file `email_service.py` at core/process/email_service.py
2. In line 12 and 13, replace `username` and `password` by your outlook account

    
 ## Images from this project
![Pic1](./images/image_1.png?raw=true)
![Pic2](./images/image_2.png?raw=true)
![Pic3](./images/image_3.png?raw=true)
![Pic4](./images/image_4.png?raw=true)
