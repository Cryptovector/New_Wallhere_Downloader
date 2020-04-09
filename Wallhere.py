from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC 
from selenium.webdriver import ActionChains 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options  
from collections import deque 
from PIL import Image
from io import BytesIO
import captcha_Solve
import collections 
import os
import time
import html
import requests
import shutil
import zipfile
import platform
import argparse
from lxml import html

Download_Folder = os.path.dirname(os.path.realpath(__file__))+'\\Image_Downloads'
Direct_Path = os.path.dirname(os.path.realpath(__file__))
Timeout_wait = 20
Sleeper = 0.2
Captcha_Trys = 60
Timout_fails = 6
Iter = int(Timeout_wait/Sleeper)


def Captcha_Solver(Img):
	Solution = captcha_Solve.Solve_captcha(Img)
	return Solution

def Download_Geckodriver(): #Windows

	#Download and extract geckodriver
	try:
		response = requests.get("https://github.com/mozilla/geckodriver/releases/")
		tree = html.fromstring(response.content)
		tree = tree.xpath('/html/body/div[4]/div/main/div[2]/div/div[3]/div[1]/div/div[2]/div[1]/div/div/a')

		if platform.architecture()[0] == '64bit':
			Zipname = "geckodriver-"+tree[0].text_content()+"-win64.zip"
		else:
			Zipname = "geckodriver-"+tree[0].text_content()+"-win32.zip"

		response = requests.get('https://github.com/mozilla/geckodriver/releases/download/' + tree[0].text_content() + "/" + Zipname, stream=True)
		if response.status_code == 200:
			with open(Zipname, 'wb') as out_file:
				shutil.copyfileobj(response.raw, out_file)
			del response
	except:	
		print("Could not Download and write newest version of Geckodriver ... ")	

	try:
		if os.path.isfile("geckodriver.exe"):
			os.remove("geckodriver.exe")
		zip = zipfile.ZipFile(Zipname)
		zip.extractall()
	except:	
		print("Could not be extracted ... ")

def Download_Ublockorigin():

	#Download Ublockorigin
	try:
		response = requests.get("https://github.com/gorhill/uBlock/releases/")
		tree = html.fromstring(response.content)
		tree = tree.xpath('/html/body/div[4]/div/main/div[2]/div/div[3]/div[1]/div/div[2]/div[1]/div/div/a')

		xpiname = 'uBlock0_'+tree[0].text_content()+'.firefox.signed.xpi'

		response = requests.get('https://github.com/gorhill/uBlock/releases/download/' + tree[0].text_content() + "/" + xpiname, stream=True)
		if response.status_code == 200:
			with open(xpiname, 'wb') as out_file:
				shutil.copyfileobj(response.raw, out_file)
	except:	
		print("Could not Download and write newest version of Ublockorigin ... ")			


def Kill_Gecko_Firefox():
	os.system("taskkill /F /im Firefox.exe")
	os.system("taskkill /F /im Geckodriver.exe")

def Init_Geckodriver(headless):
	driver = None

	try:
		options = Options()
		options.headless = headless
		profile = webdriver.FirefoxProfile()

		profile.set_preference("browser.download.folderList", 2)
		profile.set_preference("browser.download.manager.showWhenStarting", False)
		profile.set_preference("browser.download.dir", Download_Folder)
		profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "Image/PNG, Image/JPEG")
		profile.set_preference("browser.helperApps.alwaysAsk.force", False)

		driver = webdriver.Firefox(options=options,firefox_profile=profile, executable_path="geckodriver.exe")
		for root, dirs, files in os.walk(Direct_Path): #Installs all Addons in Folder
			for file in files: 
				if file.endswith('.xpi'):
					driver.install_addon(Direct_Path+'\\'+file, temporary=True)  
	except:	
		print("Could not Init Geckodriver ... ")

	return driver			

def Download_Single_Image(Imgurl, driver):
	try:
		driver.get(Imgurl)
		wait = WebDriverWait(driver, Timeout_wait)
		print("Waiting for Cloudfare ...")
		wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/img')))
		print("Site reached")
		driver.execute_script('var a = document.createElement("a");a.href = '+'"'+Imgurl+'"'+';a.download = "output.png";document.body.appendChild(a);a.click();document.body.removeChild(a);')
		print("Download image: " + Imgurl)

		Download_Output = Download_Folder + '\\output.png'
		Imagename = Download_Folder + "\\" + Imgurl.split('/')[-1].split('!d')[0]
		for i in range(Iter):
			try:
				os.rename(Download_Output, Imagename)
				return False, Imagename
			except:
				pass
			print(str(i) + " Iteration")	
			time.sleep(Sleeper)
		return True, Imagename	
	except:
		print("Could not Download image "+ Imgurl +" Retry later")
		return True, None		


def Reload_Image_Page(Imgurl, driver, i, Imgfullxpath): #Helperfunction
	if(i == Captcha_Trys-1):
		raise Exception("Too many Captcha Trys ...")
	
	driver.get(Imgurl)
	wait = WebDriverWait(driver, Timeout_wait)
	wait.until(EC.presence_of_element_located((By.XPATH, Imgfullxpath)))
	driver.find_element_by_xpath(Imgfullxpath).click()


def Download_Single_Full_Image(Imgurl, driver): #Needs Auth (Login)
	try:
		driver.get(Imgurl)
		wait = WebDriverWait(driver, Timeout_wait)
		print("Waiting for Cloudfare ...")
		Imgfullxpath = '//*[@id="hub-commonsize"]/ul/li[1]/a'
		wait.until(EC.presence_of_element_located((By.XPATH, Imgfullxpath)))
		print("Site reached")
		driver.find_element_by_xpath(Imgfullxpath).click()	

		for i in range(Captcha_Trys):
			wait = WebDriverWait(driver, Timeout_wait)
			wait.until(EC.presence_of_element_located((By.XPATH, '/html/body')))
			for y in range(Iter):
				try:
					driver.find_element_by_xpath('/html/body/form/img')
					break
				except:
					try:
						driver.find_element_by_xpath(Imgfullxpath)
						return
					except:
						pass
				print("Wait for site loading ...")		
				time.sleep(Sleeper)	
	
			print("Captcha try: "+str(i))	
			wait = WebDriverWait(driver, Timeout_wait) 
			wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/form/img')))
			png = driver.find_element_by_xpath('/html/body/form/img').screenshot_as_png
			Img = Image.open(BytesIO(png))
			Solution = Captcha_Solver(Img)

			if len(Solution) != 5:
				Reload_Image_Page(Imgurl, driver, i, Imgfullxpath)
			else:	
				Captcha = driver.find_element_by_xpath('/html/body/form/input[1]')
				Captcha.send_keys(Solution)
				driver.find_element_by_xpath('/html/body/form/input[2]').click()

				if driver.find_element_by_xpath('/html/body/div').text == "Download is excess.":
					break
				else:
					Reload_Image_Page(Imgurl, driver, i, Imgfullxpath)
			
	except:
		print("Could not Download Image: " + Imgurl + " Retry later")
		return True

	return False					


def Get_clear_Image_Url(Url, driver):
	Imgurl = None
	Imghtml = None

	try:
		driver.get(Url)
		wait = WebDriverWait(driver, Timeout_wait)
		wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'hub-photomodal')))
		for i in range(Iter):
			try:
				Imghtml = driver.find_element_by_class_name('hub-photomodal').find_element_by_xpath('a/img')
				break
			except:
				pass	
			time.sleep(Sleeper)
		Imgurl = Imghtml.get_property('src')
	except:
		print("Timout or other error for image: " + Url + " Retry later")	
		
	return Imgurl
	


def Get_Image_Urls(Url, driver):
	Pagecount = 1
	Urllist = []

	try:
		while True:
			driver.get(Url + '&page=' + str(Pagecount))
			for i in range(1,25):
				if Pagecount == 1:
					Imgxpath = '/html/body/section/div[3]/div[2]/div['+str(i)+']/a'
				else:
					Imgxpath = '/html/body/section/div[3]/div[2]/div['+str(i+1)+']/a'

				wait = WebDriverWait(driver, Timeout_wait)
				wait.until(EC.presence_of_element_located((By.XPATH, Imgxpath)))
				Imghtml = driver.find_element_by_xpath(Imgxpath)
				Urllist.append(Imghtml.get_property('href'))
				print(Imghtml.get_property('href'))

			Pagecount += 1
	except:
		pass		

	return Urllist		


def Login_Account(Username, Password, driver):
	try:
		driver.get("https://wallhere.com/de/login")
		wait = WebDriverWait(driver, Timeout_wait)
		wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div/div/div/form')))
		Userform = driver.find_element_by_xpath('/html/body/div[2]/div/div/div/form/div[1]/input')
		Passform = driver.find_element_by_xpath('/html/body/div[2]/div/div/div/form/div[2]/input')	
		Userform.send_keys(Username)
		Passform.send_keys(Password)

		driver.find_element_by_xpath('/html/body/div[2]/div/div/div/form/div[3]/button').click()
	except:
		print("Could not Login ...")	


def Wait_ImageDownload(driver): #Auth
	try:
		for i in range(Iter):
			try:
				Filename = None
				File_ID = driver.current_url.split("-")[-1].split(".")[0]

				for root, dirs, files in os.walk(Download_Folder): #Installs all Addons in Folder
					print(len(files), ' Files in Root Folder')
					for file in files:
						try:
							if not file.endswith('.part'):
								if File_ID in file:
									Filename = file
								else:	
									os.remove(Download_Folder + '\\' + file)
						except:
							pass
					break			

				New_Download_Folder = Download_Folder + '\\Comp'		
				Full_Filename = Download_Folder + '\\' + Filename
				if not os.path.isdir(New_Download_Folder):
					os.mkdir(New_Download_Folder)		
				if Filename != None:	
					New_Full_Filename = New_Download_Folder + '\\' + Filename
					if os.path.isfile(Full_Filename):
						if os.stat(Full_Filename).st_size:
							os.rename(Full_Filename, New_Full_Filename)
							print("Finish Download: "+Url[0])
							return False, New_Full_Filename
			except:
				pass
			print(str(i) + " Download Image Iteration")	
			time.sleep(Sleeper)
			if(i == Iter-1):
				return True, None
	except:
		return True, None				
	

def Test_Image(Filename):	
	try:		
		image = Image.open(Filename)
		image.verify()
	except:
		try:
			del image
			os.remove(Filename)
			return True
		except:
			return True
			print("Could not Delete broken Image ...")
	return False

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Wallhere Downloader')
	parser.add_argument('-K','--Kill', action='store_false')
	parser.add_argument('-I','--Init', action='store_false')
	parser.add_argument('-H','--Noheadless', action='store_false')
	parser.add_argument('-i','--Image', action='store_false')
	parser.add_argument('-k','--Keyword', action='store_false')
	parser.add_argument('-l','--Login', action='store_false')
	parser.add_argument('-u', '--Url',
		action="store", dest="Url",
		help="Url for Image or Keyword", default="")
	parser.add_argument('-d', '--destination',
		action="store", dest="destination",
		help="Path for Image files", default="")	
	parser.add_argument('-us', '--Username',
		action="store", dest="Username",
		help="Username for Auth", default="")	
	parser.add_argument('-pa', '--Password',
		action="store", dest="Password",
		help="Pass for Auth", default="")	

	args = parser.parse_args()

	Download_Folder = args.destination	

	if not args.Init:
		Download_Geckodriver()
		Download_Ublockorigin()
	
	if not args.Kill:
		Kill_Gecko_Firefox()

	driver = Init_Geckodriver(args.Noheadless)	

	if not args.Login:
		Login_Account(args.Username, args.Password, driver)
		print("login ...")
		Auth = True
	else:
		Auth = False

	if (args.Image ^ args.Keyword):

		Failed_deque = collections.deque()
		
		if not args.Keyword:
			Urllist = Get_Image_Urls(args.Url, driver)
			print("Download: " + str(len(Urllist)) + " Images")

			for Url in Urllist:
				Failed_deque.append([Url, 0])

		if not args.Image:
			Failed_deque.append([args.Url, 0])		

		while len(Failed_deque):
			Url = Failed_deque.popleft()
			if Url[1] > Timout_fails:
				break
			if Auth:	
				if Download_Single_Full_Image(Url[0], driver):
					Failed_deque.append([Url[0], Url[1]+1])
				else:
					Imgpath = Wait_ImageDownload(driver)
					if Imgpath[0]:
						Failed_deque.append([Url[0], Url[1]+1])
					else:
						if Test_Image(Imgpath[1]):
							Failed_deque.append([Url[0], Url[1]+1])	
			else:
				Clearimgurl = Get_clear_Image_Url(Url[0], driver)
				if Clearimgurl == None:
					Failed_deque.append([Url[0], Url[1]+1])
				else:
					Imgpath = Download_Single_Image(Clearimgurl, driver)	
					if Imgpath[0]:
						Failed_deque.append([Url[0], Url[1]+1])
					else:
						if Test_Image(Imgpath[1]):
							Failed_deque.append([Url[0], Url[1]+1])
						else:	
							print("Finish Download: "+Url[0])

			if len(Failed_deque):			
				print("deque lengt: "+str(len(Failed_deque))+" Last deque: "+Failed_deque[-1][0]+" Trys: "+str(Failed_deque[-1][1]))
			
	else:	
		print("Usage: use -i or -k")

	try:
		driver.quit()
	except:
		pass