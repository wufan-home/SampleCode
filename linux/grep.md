# Grep

**Grep with sudo**: Sometimes, grep cannot access the folder with only root permissions. Use the following command:

```bash
sudo /usr/bin/find <path> -name <name_pattern> | xargs grep -nir <pattern>
```
