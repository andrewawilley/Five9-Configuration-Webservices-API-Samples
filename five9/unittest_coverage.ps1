# a powershell script that runs 
coverage run -m unittest discover -s tests -p "test*.py" -v


# if argument "donotopenhtml" is passed, do not open the htmlcov\index.html
if ($args[0] -ne "donotopenhtml") {
    coverage html
    start htmlcov\index.html
}
