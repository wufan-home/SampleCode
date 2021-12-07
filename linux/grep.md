# Grep

**Grep with sudo**.

Sometimes, grep cannot get the information from the folder with the root permission only. Use the following command:

```bash
sudo /usr/bin/find <path> -name <name_pattern> | xargs grep -nir <pattern>
```
