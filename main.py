from database import Database

class Main:
    def __init__(self):
        self.database = Database()
        self.auth_selection = None
        self.restaurant_selection = None
        self.program_selection = None
        self.user_table = 'user'
        self.dish_table = 'dish'
        self.order_table = 'order_'
        self.order_dish_table = 'order_dish'
        self.user = None

    def show_auth_menu(self):
        print()
        print('1. Iniciar sesión')
        print('2. Registrarse')
        print('3. Salir del programa')
        print()

    def show_restaurant_menu(self):
        print()
        print('1. Ver platillos')
        print('2. Crear platillo')
        print('3. Realizar pedido')
        print('4. Ver pedidos realizados')
        print('5. Ver perfil')
        print('6. Editar perfil')
        print('7. Cerrar sesión')
        print()

    def validate_user_auth_selection(self, selection):
        return isinstance(selection, int) and selection > 0 and selection < 4

    def validate_user_restaurant_selection(self, selection):
        return isinstance(selection, int) and selection > 0 and selection < 8

    def handle_user_auth_selection(self):
        self.auth_selection = int(input('¿Qué opción deseas?: '))
        while not self.validate_user_auth_selection(self.auth_selection):
            print('La opción ingresada en incorrecta, intenta nuevamente.')
            self.auth_selection = int(input('¿Qué opción deseas?: '))
        self.handle_auth_menu_options()

    def handle_user_restaurant_selection(self):
        self.restaurant_selection = int(input('¿Qué opción deseas?: '))
        while not self.validate_user_restaurant_selection(self.restaurant_selection):
            print('La opción ingresada en incorrecta, intenta nuevamente.')
            self.restaurant_selection = int(input('¿Qué opción deseas?: '))
        self.handle_restaurant_menu_options()

    def handle_auth_menu_options(self):
        opts = {
            '1': self.login,
            '2': self.register
        }
        opts[str(self.auth_selection)]()

    def handle_restaurant_menu_options(self):
        opts = {
            '7': self.logout
        }
        opts[str(self.restaurant_selection)]()

    def register(self):
        user_columns = self.database.get_columns_by_table(self.user_table)
        del user_columns[0]
        del user_columns[-1]
        data = [input(f'{x}: ') for x in user_columns]
        new_user = self.database.create(self.user_table, tuple(data))
        if self.database.validate_not_error(new_user):
            print("Te has registrado correctamente con el ID: ", new_user)
            print("Ahora inicia sesión")
        else:
            print(new_user.message)

    def login(self):
        email = input('Ingresa tu correo electrónico: ')
        password = input('Ingresa tu contraseña: ')

        email_db = self.database.get_one(self.user_table, email, 'email')
        if self.database.validate_get_one_result(email_db):
            password_db = self.database.get_one(self.user_table, password, 'password')
            if self.database.validate_get_one_result(password_db):
                if email_db[0] == password_db[0]:
                    logged_in_update = self.database.update(self.user_table, 'is_logged', 1, email_db[0])
                    if self.database.validate_create_update_result(logged_in_update):
                        user = self.database.get_one(self.user_table, email_db[0])
                        self.set_user(user)
                        print("Has iniciado sesión correctamente")
                    else:
                        print("Algo falló al guardar sesión")
                else:
                    print("Credenciales incorrectas")
                    return False
            else:
                print("Credenciales incorrectas")
                return False
        else:
            print("No hay ningún usuario vinculado a ese correo electrónico")
            return False

    def logout(self):
        logged_in_logout = self.database.update(self.user_table, 'is_logged', 0, self.user[0])
        if self.database.validate_create_update_result(logged_in_logout):
            self.set_user(None)
            print('Cerrarse sesión correctamente')

    def set_user(self, user):
        self.user = user

    def entrypoint(self):
        while self.program_selection != 1:
            if self.user:
                self.show_restaurant_menu()
                self.handle_user_restaurant_selection()
            else:
                self.show_auth_menu()
                self.handle_user_auth_selection()


main = Main()
main.entrypoint()
