from instagram_private_api import Client
import instaloader
from instaloader import  Profile
import csv
from datetime import datetime
import time
import sys

#Creating Useful Functions
def get_instaloader_details(target_username, username, password):
    print("Fetching User details")
    L = instaloader.Instaloader()
    L.login(username, password)
    profile = Profile.from_username(L.context, target_username)
    following_list = profile.get_followees()
    followings_list = []
    print("Getting Following List")
    for following in following_list:
        followings_list.append(following.username)

    print(f"total following count:{following_list.count}")
    print("Fetching Followers List")
    follower_list = profile.get_followers()
    followers_list = []
    for follower in follower_list:
        followers_list.append(follower.username)
    print("Done")
    return followings_list, followers_list

def get_instagram_info(target_username, username, password):
    api = Client(username, password)

    try:
        print("Fetching Top Posts")

        user_id = api.username_info(target_username)["user"]["pk"]
        data["username"] = target_username
        print(f"Target username userid:{user_id}")
        user_info = api.user_info(user_id)

        followers_count = user_info["user"]["follower_count"]
        following_count = user_info["user"]["following_count"]
        profile_image = user_info["user"]["hd_profile_pic_url_info"]["url"]
        post_count = user_info["user"]["media_count"]
        is_private  = user_info["user"]['is_private']

        data["follower_count"]= followers_count
        data["following_count"]= following_count
        data["profilephoto"] = profile_image
        data["num_posts"] = post_count
        data["is_Private"] = is_private

        # Get the top 5 posts based on likes and comments
        top_posts_likes = get_top_posts(api, user_id, key="like_count")
        top_posts_comments = get_top_posts(api, user_id, key="comment_count")

        list_likes = []
        data["top_posts_by_like"] = list_likes
        for post in top_posts_likes:
            link = "www.instagram.com/p/"+post["code"]+"/"
            list_likes.append(link)

        list_comments = []

        for post in top_posts_comments:
            link = "www.instagram.com/p/"+post["code"]+"/"
            list_comments.append(link)

        return list_likes, list_comments
    except Exception as e:
        return {"error": str(e)}

def get_top_posts(api, user_id, key="like_count"):
    posts = api.user_feed(user_id)['items']
    sorted_posts = sorted(posts, key=lambda x: x[key], reverse=True)[:5]
    return [{"code": post['code'], "like_count": post['like_count'], "comment_count": post['comment_count']} for post in sorted_posts]


if __name__ == "__main__":
    start_time = time.time()
    target_username = input("Enter the Username: ")
    username = None #type your username here
    password = None #type your password here

#get lists
    following, followers = get_instaloader_details(target_username, username, password)

    # Sample data (replace this with your actual data)
    data = {
        'username': 'JohnDoe',
        'profilephoto': 'https://example.com/johndoe',
        'follower_count': 1000,
        'following_count': 500,
        'num_posts': 50,
        'is_Private': True,
        'top_posts_by_like':None,
        'top_posts_by_comments':None,
        'following_list':following,
        'followers_list':followers
    }
    top_liked_posts, top_commented_posts = get_instagram_info(target_username, username, password)
    data["top_posts_by_like"] = top_liked_posts
    data["top_posts_by_comments"] = top_commented_posts

    #creating a csv file
    # Get the current time
    current_time = datetime.now().time()
    # Format the time as "hhmm"
    time_string = current_time.strftime("%H%M")

    print("creating CSV")
    for i in range(5):
        time.sleep(.5)
        sys.stdout.write('.')
        sys.stdout.flush()

    # CSV field names
    field_names = [
        'username', 'profilephoto', 'follower_count', 'following_count',
        'num_posts', 'is_Private', 'top_posts_by_like',
        'top_posts_by_comments', 'following_list', 'followers_list'
    ]

    # CSV file path
    csv_file_path = f'{target_username}_output_{time_string}.csv'
    # Write data to CSV file
    with open(csv_file_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_names)

        # Write header
        writer.writeheader()

        # Determine the maximum length among the lists
        max_length = max(
            len(data['followers_list']),
            len(data['following_list'])
        )
        # Write common data and items from lists in separate rows

        row_data = [
        data['username'],
        data['profilephoto'],
        data['follower_count'],
        data['following_count'],
        data['num_posts'],
        data['is_Private'],
        ]
            # Write data from lists in separate rows
        for i in range(max_length):
            if i == 0:
                row_data = row_data.copy()
            else:
                row_data = ["", "", '', '', '', '']
            # Add data from 'top_posts_by_like'
            if i < len(data['top_posts_by_like']):
                row_data.append(data['top_posts_by_like'][i])
            else:
                row_data.append('')
            # Add data from 'top_posts_by_comments'
            if i < len(data['top_posts_by_comments']):
                row_data.append(data['top_posts_by_comments'][i])
            else:
                row_data.append('')
            if i < len(data['following_list']):
                row_data.append(data['following_list'][i])
            else:
                row_data.append('')

            if i < len(data['followers_list']):
                row_data.append(data['followers_list'][i])
            else:
                row_data.append('')

            row_data_ = dict(zip(field_names, row_data))
            writer.writerow(row_data_)

    end_time = time.time()
    print(f'CSV file "{csv_file_path}" created successfully.')
    # Calculate and print the total time taken
    total_time = end_time - start_time
    print(f"Processing completed. Total time taken: {total_time:.2f} seconds.")
