from ldap3 import Server, Connection, ALL, MODIFY_REPLACE
import json
import sys

# AD Server details
AD_SERVER = 'ldap://your.ad.server'
AD_USER = 'CN=Admin,CN=Users,DC=example,DC=com'
AD_PASSWORD = 'your_password'
BASE_DN = 'DC=example,DC=com'

def connect_to_ad():
    """Establish connection to Active Directory"""
    server = Server(AD_SERVER, get_info=ALL)
    connection = Connection(server, user=AD_USER, password=AD_PASSWORD, auto_bind=True)
    return connection

def create_user(connection):
    """Create a new user in Active Directory"""
    username = input("Enter the username: ")
    password = input("Enter the password: ")
    first_name = input("Enter the first name: ")
    last_name = input("Enter the last name: ")

    user_dn = f'CN={username},CN=Users,{BASE_DN}'
    attributes = {
        'objectClass': ['top', 'person', 'organizationalPerson', 'user'],
        'sAMAccountName': username,
        'userPrincipalName': f'{username}@example.com',
        'givenName': first_name,
        'sn': last_name,
        'userPassword': password
    }

    connection.add(user_dn, attributes=attributes)
    connection.commit()
    print(f'User {username} created successfully.')

def delete_user(connection):
    """Delete a user from Active Directory"""
    username = input("Enter the username to delete: ")
    user_dn = f'CN={username},CN=Users,{BASE_DN}'
    
    connection.delete(user_dn)
    connection.commit()
    print(f'User {username} deleted successfully.')

def update_user(connection):
    """Update a user's attribute in Active Directory"""
    username = input("Enter the username to update: ")
    attribute = input("Enter the attribute to update (e.g., givenName, sn): ")
    new_value = input(f"Enter the new value for {attribute}: ")
    
    user_dn = f'CN={username},CN=Users,{BASE_DN}'
    connection.modify(user_dn, {attribute: [(MODIFY_REPLACE, [new_value])]})
    connection.commit()
    print(f'User {username} updated successfully.')

def get_user(connection):
    """Get details of a user from Active Directory"""
    username = input("Enter the username to get details: ")
    user_dn = f'CN={username},CN=Users,{BASE_DN}'
    connection.search(user_dn, '(objectClass=person)', attributes=['givenName', 'sn', 'sAMAccountName', 'userPrincipalName'])

    if connection.entries:
        user = connection.entries[0]
        print(json.dumps(user.entry_attributes_as_dict, indent=2))
    else:
        print(f'User {username} not found.')

def list_all_users(connection):
    """List all users in Active Directory"""
    connection.search(BASE_DN, '(objectClass=user)', attributes=['givenName', 'sn', 'sAMAccountName', 'userPrincipalName'])

    if connection.entries:
        for entry in connection.entries:
            print(json.dumps(entry.entry_attributes_as_dict, indent=2))
    else:
        print('No users found.')

def add_user_to_group(connection):
    """Add a user to a group"""
    username = input("Enter the username to add to a group: ")
    group_name = input("Enter the group name: ")

    user_dn = f'CN={username},CN=Users,{BASE_DN}'
    group_dn = f'CN={group_name},CN=Users,{BASE_DN}'
    
    connection.modify(group_dn, {'member': [(MODIFY_REPLACE, [user_dn])]})
    connection.commit()
    print(f'User {username} added to group {group_name}.')

def remove_user_from_group(connection):
    """Remove a user from a group"""
    username = input("Enter the username to remove from a group: ")
    group_name = input("Enter the group name: ")

    user_dn = f'CN={username},CN=Users,{BASE_DN}'
    group_dn = f'CN={group_name},CN=Users,{BASE_DN}'
    
    connection.modify(group_dn, {'member': [(MODIFY_REPLACE, [user_dn])]})
    connection.commit()
    print(f'User {username} removed from group {group_name}.')

def main_menu():
    """Display the main menu and handle user input"""
    print("\nActive Directory Automation Menu:")
    print("1. Create a new user")
    print("2. Delete a user")
    print("3. Update a user")
    print("4. Get user details")
    print("5. List all users")
    print("6. Add user to group")
    print("7. Remove user from group")
    print("8. Exit")

def run():
    """Main function to run the AD tasks"""
    connection = connect_to_ad()

    while True:
        main_menu()
        choice = input("Choose an option (1-8): ")

        if choice == '1':
            create_user(connection)
        elif choice == '2':
            delete_user(connection)
        elif choice == '3':
            update_user(connection)
        elif choice == '4':
            get_user(connection)
        elif choice == '5':
            list_all_users(connection)
        elif choice == '6':
            add_user_to_group(connection)
        elif choice == '7':
            remove_user_from_group(connection)
        elif choice == '8':
            print("Exiting the program.")
            connection.unbind()
            sys.exit()
        else:
            print("Invalid option. Please choose again.")

if _name_ == '_main_':
    run()
