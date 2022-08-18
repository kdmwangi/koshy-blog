def number_of_times(f):

    def wrapper_func(a,b):
                print(f(a,b))
                print(f(a,b))
    #     or return type


    return wrapper_func

@number_of_times
def add(a,b):
    return a+b


add(2,3)
# syntax for a python decorator is
# def name_of_the_decorator(name_of_the function):
#     def wrapper_function(here goes any arguments that the function might take):
#         what you intend to do with the function that ou will receive
#     return the_wrapper_function
# is similar to calling the wrapper function



# data relationships in the database between posts and a particular user

class User:
    def __init__(self, name, email, password,title,subtitle,body):
        self.name = name
        self.email = email
        self.password = password
        self.posts = BlogPost(title,subtitle,body)


class BlogPost:
    def __init__(self, title, subtitle, body):
        self.title = title
        self.subtitle = subtitle
        self.body = body


new_user = User(
    name="Angela",
    email="angela@email.com",
    password=123456,
            title="Life of Cactus",
            subtitle="So Interesting",
            body="blah blah"

)

print(new_user.posts.title)
