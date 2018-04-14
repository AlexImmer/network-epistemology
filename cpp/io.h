#ifndef CPP_IO_H
#define CPP_IO_H

#include <unordered_map>
#include <string>
#include <vector>

#include <boost/serialization/string.hpp>
#include <boost/archive/binary_oarchive.hpp>
#include <boost/archive/binary_iarchive.hpp>

class PubInfo {
public:
    std::string id;
    int year;
    std::string title;
    PubInfo() {}
    PubInfo(std::string _id, int _year, std::string _title) : id(_id), year(_year), title(_title) {}
    template<class Archive>
    void serialize(Archive & ar, const unsigned int version) {
        ar & id;
        ar & year;
        ar & title;
    }
};

const int MAXV = 5000000;

const int SPREADS = 0;
const int CITES = 1;
const int COLLABORATES = 2;
const int PUBLISHES = 3;
const int AUTHORED = 4;

// Data to be serialized
extern int V;
extern std::unordered_map<std::string, int> author_ids;
extern std::unordered_map<std::string, int> publication_ids;
extern std::vector<std::string> names;
extern std::vector<PubInfo> pub_infos;
extern std::vector<std::vector<std::pair<int, int>>> adj;
// ----------------------------------------------------------


void read_authors(const std::string &path);
void read_publications(const std::string &path);
void read_edges(std::string path, std::string file_name, int edge_type);

#endif //CPP_IO_H
