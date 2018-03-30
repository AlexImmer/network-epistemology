#ifndef CPP_IO_H
#define CPP_IO_H

#include <unordered_map>
#include <string>
#include <vector>

struct PubInfo {
    std::string id;
    int year;
    PubInfo() {}
    PubInfo(std::string _id, int _year) : id(_id), year(_year) {}
};

const int MAXV = 5000000;

extern std::unordered_map<std::string, int> author_ids;
extern std::unordered_map<std::string, int> publication_ids;
extern std::vector<std::string> names;
extern std::vector<PubInfo> pub_infos;
extern std::vector<std::pair<int, int>> adj[MAXV];

void read_authors(const std::string &path);
void read_publications(const std::string &path);
void read_edges(std::string path, std::string file_name, int edge_type);

#endif //CPP_IO_H
