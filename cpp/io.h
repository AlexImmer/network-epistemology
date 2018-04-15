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

struct Edge {
    int next;
    int type;
    int year;

    Edge() {}
    Edge(int _next, int _type) : next(_next), type(_type), year(0) {}
    Edge(int _next, int _type, int _year) : next(_next), type(_type), year(_year) {}

    template<class Archive>
    void serialize(Archive & ar, const unsigned int version) {
        ar & next;
        ar & type;
        ar & year;
    }
};

const int MAXV = 5000000;

const int SPREADS = 1 << 0;
const int CITES = 1 << 1;
const int COLLABORATES = 1 << 2;
const int PUBLISHES = 1 << 3;
const int AUTHORED = 1 << 4;

// Data to be serialized
extern int V;
extern std::unordered_map<std::string, int> author_ids;
extern std::unordered_map<std::string, int> publication_ids;
extern std::unordered_map<int, std::string> names;
extern std::unordered_map<int, PubInfo> pub_infos;
extern std::vector<std::vector<Edge>> adj;
// ----------------------------------------------------------


void read_authors(const std::string &path);
void read_publications(const std::string &path);
void read_edges(std::string path, std::string file_name, int edge_type);

#endif //CPP_IO_H
