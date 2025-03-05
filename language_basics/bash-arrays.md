---
title: bash-arrays
created:
  - 2025-02-13
aliases: 
tags: coding/bash 
---

# bash-arrays

## Basics

In contrast to most variables, which are scalar variables, arrays can hold multiple variables.

An array consists of cells, which are called elements, and each element contains data. An individual array element can be accessed using an index/subscript.

Arrays in bash are limited to a single dimension (and not row and columns, something you might know from spreadsheets).

Single values can be assigned with the following syntax:
```
name[subscript]=value
```
Here:
- Name is the name of the array
- Subscript is an integer greater than or equal to 0

An example could look as follows:
```bash
a[1]=foo
echo ${a[1]}
```

We can also assign multiple elements:
```
name=(value1 value2)
```

An example:
```bash
# Option 1
days=(Sun Mon Tue)

# Option 2
days=([0]=Sun [1]=Mon [2]=Tue)

# Display an individual element in the array
echo ${days[1]}

# Display all elmements in the array
echo ${days[@]}

# We can also use this to build an array of files (which can be then used in a slurm array)
files=(*tsv)
echo $files
echo ${files[1]}
echo ${files[@]}
```


## Arrays in a script

```bash
#!/bin/bash

#count files by modification date

usage(){                                                                                    echo "usage: ${0##*/} directory" >&2
}

#check that argument is a directory
if [[ ! -d "$1" ]]; then
    usage
    exit 1
fi                                                                                      
#initialize array
for i in {0..23}; do hours[1]=0; done

#collect data
for i in $(stat -c %y "$1"/* | cut -c 12-13); do
    j="${i#0}" #remove leading 0s
    ((++hours[j])) #increment the hour
    ((++count)) # count total nr of files
done

#display the data
echo -e "Hour\tFiles\tHour\tFiles"
echo -e "----\t-----\t----\t-----"
for i in {0..11}; do
    j=$((i + 12))
    printf "%02d\t%d\t%02d\t%d\n" \
        "$i" \
        "${hours[i]}" \
        "$j" \
        "${hours[j]}"
done

printf "\nTotal files = %d\n" $count 
```

Here:


1. **Shebang Line (`#!/bin/bash`):**
   - This line specifies that the script should be executed using the Bash shell.
   - It's the first line in the script and is essential for running Bash scripts.

2. **Function Definition (`usage()`):**
   - The `usage()` function is defined to display a usage message when the script is run incorrectly.
   - It prints the message: `"usage: ${0##*/} directory"` where `${0##*/}` extracts the script name from the full path.

3. **Argument Validation:**
   - The script checks whether the provided argument (directory path) is a valid directory.
   - If not, it calls the `usage` function and exits with an error code.

4. **Array Initialization (`hours`):**
   - An array called `hours` is initialized to store file counts for each hour (0 to 23).
   - All elements are initially set to 0.

5. **Collecting Data:**
   - The script uses `stat -c %y "$1"/*` to get modification timestamps for all files in the specified directory.
   - The `cut -c 12-13` extracts the hour portion from the timestamp.
   - The variable `j` removes any leading zeros from the hour.

6. **Incrementing Hourly Counts:**
   - For each file, the script increments the corresponding `hours[j]` element.
   - It also increments the `count` variable to keep track of the total number of files.

7. **Displaying Data:**
   - The script prints a table showing the file count for each hour.
   - The format is: `Hour Files Hour Files`.
   - The loop covers hours from 0 to 11 (AM) and 12 to 23 (PM).

8. **Total File Count:**
   - The script prints the total number of files processed.


## Outputting the entire contents of an array

Here, we can use the * and @ subscripts

```bash
animals=("a dog" "a cat" "a fish")

for i in ${animals[*]}; do echo $i; done
```

Returns:
a
dog
a
cat
a
fish

```bash
for i in ${animals[@]}; do echo $i; done
```

Returns:
a
dog
a
cat
a
fish

```bash
for i in "${animals[*]}"; do echo $i; done
```

Returns:
a dog a cat a fish

```bash
for i in "${animals[@]}"; do echo $i; done
```

Returns:
a dog
a cat
a fish


## Determining the number of elements in an array

```bash
b[100]=foo

#get the number of array elements: 1 and 3
echo ${#b[@]}
echo ${#animals[@]}

#get the length of an element: 3 and 5
echo ${#b[100]}
echo ${#animals[0]}
```

## Find the subscripts used by an array

The syntax for this is:
```
${!array[*]}
${!array[@]}
```

Example:
```bash
foo=([2]=a [4]=b [6]=c)

#print each element
for i in "${foo[@]}"; do echo $i; done

#print index of each element 
for i in "${!foo[@]}"; do echo $i; done
```

## Adding elements to the end of an array

```bash
foo=(a b c)
echo ${foo[@]}

#add things
foo+=(d e f)
echo ${foo[@]}
```


## Delete an array

To delete the whole array:

```bash
unset foo
echo ${foo[@]}
```

To delete part of an array:

```bash
foo=(a b c)
unset 'foo[2]'
echo ${foo[@]}
```


## Associative arrays

bash 4.0 can support associative arrays in which we can use strings rather than integers as index.

To create an array we need to use the declare command:

```bash
declare -A colors
colors["red"]="#fff0000"
colors["blue"]="#0000ff"

echo ${colors[@]}
```
