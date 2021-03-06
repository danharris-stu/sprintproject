'''
Online Shopping System
This program parses shopping data from a file to allow the user to pick items and quantities and then displays
these in a formatted receipt. The receipt is then stored in a file and uploaded to an S3 bucket.

Authors: Daniel Harris, Nicholas Hodder and Annette Clarke
'''
import os.path
from os import path
import boto3


def add_products():
    '''
        Description: Loops to add products to the product.dat file until user exits, verifies each entry.
        Parameters: None
        Returns: Nothing
    '''
    f=open("products.dat","a")
    more_products = True
    while more_products == True:
        new_product = input("Enter product name to add to the file: ")
        new_product = new_product.strip()
        if not new_product.isalnum():
            print("Error: Product name must be alphanumeric.")
            continue
        while True:
            try:
                new_price = float(input("Enter the price of the product: $"))
            except:
                print("Error: Must only enter the price of the product, example: 9.99")
                continue
            break
        while True:
            try:
                new_quantity = int(input("Enter the quantity of the product available: "))
            except:
                print("Error: Must only enter the quantity of the product, example: 15")
                continue
            break
        
        f.write("{}:{}:{}\n".format(new_product.lower(),new_price,new_quantity))
        print("Product added!")
        again = input("Are there more products to add? 'Y' for yes, or any other input (including blank) to finish: ")
        if again.upper() == 'Y':
            continue
        else:
            more_products = False
            break
    f.close()
    return


def make_receipt(receipt):
    '''
        Description: Generates a formatted receipt of all purchased items, displays receipt to the user and saves it as a text file
        Parameters: 
            receipt - Dictionary containing all purchased product names and quantity,price attributes
        Returns: Nothing
    '''
    HST = 0.15
    subtotal = 0
    total = 0
    f=open("receipt.txt","w")
    #Print the receipt
    print("\n\nRECEIPT\n\n")
    f.write("RECEIPT\n\n")
    
    #Format the receipt output for each item being purchased
    for product_name in receipt:
        quantity = receipt[product_name]['quantity']
        price = receipt[product_name]['price']
        formatted_product = "{} * {}".format(product_name.upper(), quantity)
        formatted_price = "${:.2f}".format(price)
        final = "{:<20}{:>10}\n".format(formatted_product, formatted_price)
        print(final)
        f.write(final)
        subtotal = subtotal + float(receipt[product_name]['price'])
        
    sub_str = "${:.2f}".format(subtotal)    
    hst_str = "${:.2f}".format(subtotal*HST)
    total_str = "${:.2f}".format(subtotal + (subtotal*HST))
    
    #Display the receipt totals
    print("\n\n{:<20}{:>10}".format("SUBTOTAL:", sub_str))
    print("{:<20}{:>10}".format("HST:", hst_str))
    print("{:<20}{:>10}".format("TOTAL:", total_str))
    #Save the receipt totals to text file
    f.write("\n{:<20}{:>10}\n".format("SUBTOTAL:", sub_str))
    f.write("{:<20}{:>10}\n".format("HST:", hst_str))
    f.write("{:<20}{:>10}".format("TOTAL:", total_str))
    f.close()
    return


def user_file():
    '''
        Description: Initializes a file for user to add products
        Parameters: None
        Returns: Nothing
    '''
    f=open("products.dat","w")
    f.close()
    add_products()
    print("User file has been created.")
    return


def purchase_item(products,receipt):
    '''
        Description: Allows user to purchase items from the product list, verifies input and then adds purchase to a receipt
        Parameters: 
            products - Dictionary containing all available product names and quantity/price attributes
            receipt - Dictionary containing all purchased product names and quantity/price attributes
        Returns:
            products - Updated with new quantity of purchased item
            receipt - Updated with new product purchased, with quantity and total price attributes
    '''
    #Input and validate user entry for product to purchase
    while True:
        product_name = input("What product would you like to buy? ")
        product_name = product_name.strip()
        if product_name.lower() not in products:
            print("Error: Product entered is not available, please try again.")
            continue
        else:
            break
    price = [i for i in products[product_name].keys()][0]
    quantity = [i for i in products[product_name].values()][0]
    print("{} costs ${} per item. There are {} left in stock.".format(product_name, price,quantity))
    
    #Input and validate user entry for quantity to purchase
    while True:
        try:
            number_purchased=int(input("How many would you like to purchase? Enter 0 to cancel: "))
        except:
            print("Error: Please enter an integer quantity.")
            continue
        if number_purchased == 0:
            print("Quantity 0 selected, cancelling product purchase.")
            break
        elif number_purchased < 0 or number_purchased > int(quantity):
            print("Sorry, that quantity is invalid. Please try again")
            continue
        #Calculate total price for this item, then ask to confirm
        item_total=float(price)*(number_purchased)
        confirm = input("Your total for this item is ${:.2f}. Enter any input (including blank) to confirm, or 'NO' to cancel this item.".format(item_total))
        if confirm.upper() == "NO":
            print("Please enter a new quantity. ")
            continue
        break
     
    #Update product quantity
    if not number_purchased == 0:
        #Failed to access key to update value, commented out temporarily
        #products[product_name][1] = products[product_name][1] - number_purchased
        
        if product_name in receipt:
            print("Updated old product quantity purchased with the new quantity.")
        receipt[product_name] = {'price':item_total,'quantity':number_purchased}
    return products, receipt
            
    
    
def sample_file():
    '''
        Description: Creates a products.dat file containing static elements
        Parameters: None
        Returns: Nothing
    '''
    f=open("products.dat","w")
    f.write("frozen pizza:9.99:15\n")
    f.write("potatoes:6.97:20\n")
    f.write("chicken:10.99:15\n")
    f.write("orange juice:4.50:7\n")
    f.write("cheesestrings:6.58:10\n")
    f.write("lasagne:10.99:5\n")
    f.write("steak:26.99:6\n")
    f.write("beer:15.99:10\n")
    print("Sample file generated.")
    f.close()
    return
   
    
def get_products():
    '''
        Description: Opens the file containing product info, imports all products with attributes from within
        Parameters: None
        Returns: A dictionary, 'products' containing the imported product info
    '''
    f=open("products.dat")
    products=dict()
    for line in f:
        items=line.strip("\n").split(':')
        products.update({items[0]:dict()})
        number_of_items=len(items)
        for i in range(1,number_of_items-1,2):
            if items[0] in products.keys():
                products[items[0]].update({items[1]:items[i+1]})  
    f.close()
    return products
    
    
        
    
if __name__ == "__main__":
    #Check for 'products.dat' prompt for user made file, or sample file to be used in the program.
    if not path.exists("products.dat"):
        file_choice = input("No products file found.\nType 'create' to make your own, or any other input (including blank) to use a sample file:  ")
        if file_choice.lower() == 'create':
            user_file()
        else:
            sample_file()
    else:
        print("Found 'products.dat'.")
        
    #Retrieve list of products
    products = get_products()
    
    #Display greeting and list all available products from products.dat
    print ("Hello! Welcome to Billy Bob's Bargain Bonanza! The products we have for sale are as follows:  \n\n")
    for product_name in products:
        print(product_name.upper() + ':')

        for price in products[product_name]:
            print ("Price: ${}".format (price))
        
        for quantity in products[product_name].values():
            print ("Quantity Remaining: {}\n".format(quantity))
            
    receipt = dict()
     
    #Prompt users to add more products until they break    
    while True:
        products, receipt = purchase_item(products, receipt)
        add_another = input("Enter 'MORE' to add purchase another product, or any other input (including blank) to stop: ")
        if add_another.upper() == 'MORE':
            continue
        else:
            break
        
    #Display the formatted receipt, and save it as receipt.txt    
    make_receipt(receipt)
    
    #Upload receipt to S3 bucket
    s3 = boto3.client('s3')
    s3.upload_file('receipt.txt', 'myreceiptbucket', 'receipt.txt')
    
    
        


    