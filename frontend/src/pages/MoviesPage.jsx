import { useState, useEffect } from "react";
import {
  getMovies,
  createMovie,
  updateMovie,
  getCategories,
  getMovieCopies,
  addMovieCopies,
} from "../api/moviesApi";
import Modal from "../components/Modal";
import { IconPlus, IconSearch, IconFilm, IconDisc } from "../components/Icons";

const EMPTY_FORM = {
  title: "",
  director: "",
  actors: "",
  country: "",
  release_year: new Date().getFullYear(),
  age_rating: 0,
  description: "",
  dubbing_languages: "",
  category_id: "",
  price: 0,
};

export default function MoviesPage() {
  const [movies, setMovies] = useState([]);
  const [categories, setCategories] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [showAddModal, setShowAddModal] = useState(false);
  const [editMovie, setEditMovie] = useState(null);
  const [form, setForm] = useState(EMPTY_FORM);
  const [saving, setSaving] = useState(false);

  const [copiesMovie, setCopiesMovie] = useState(null);
  const [copies, setCopies] = useState([]);
  const [copiesCount, setCopiesCount] = useState(1);
  const [copiesMediaType, setCopiesMediaType] = useState("DVD");
  const [addingCopies, setAddingCopies] = useState(false);

  const load = () => {
    setLoading(true);
    Promise.all([getMovies(), getCategories()])
      .then(([m, c]) => {
        setMovies(m);
        setCategories(c);
      })
      .catch(() => setError("Ошибка загрузки"))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const filtered = movies.filter(
    (m) =>
      m.title.toLowerCase().includes(search.toLowerCase()) ||
      m.director.toLowerCase().includes(search.toLowerCase()),
  );

  const openAdd = () => {
    setForm(EMPTY_FORM);
    setEditMovie(null);
    setShowAddModal(true);
  };
  const openEdit = (m) => {
    setForm({
      title: m.title,
      director: m.director,
      actors: m.actors,
      country: m.country,
      release_year: m.release_year,
      age_rating: m.age_rating,
      description: m.description,
      dubbing_languages: m.dubbing_languages,
      category_id: m.category_id,
      price: m.price,
    });
    setEditMovie(m);
    setShowAddModal(true);
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError("");
    try {
      const payload = {
        ...form,
        release_year: +form.release_year,
        age_rating: +form.age_rating,
        price: +form.price,
        category_id: +form.category_id,
      };
      if (editMovie) {
        await updateMovie(editMovie.id, payload);
      } else {
        await createMovie(payload);
      }
      setShowAddModal(false);
      load();
    } catch (e) {
      setError(e.response?.data?.detail || "Ошибка сохранения");
    } finally {
      setSaving(false);
    }
  };

  const openCopies = async (movie) => {
    setCopiesMovie(movie);
    setCopiesMediaType("DVD");
    const data = await getMovieCopies(movie.id);
    setCopies(data);
  };

  const handleAddCopies = async () => {
    setAddingCopies(true);
    try {
      await addMovieCopies(copiesMovie.id, copiesCount, copiesMediaType);
      const data = await getMovieCopies(copiesMovie.id);
      setCopies(data);
      load();
    } finally {
      setAddingCopies(false);
    }
  };

  const catName = (id) => categories.find((c) => c.id === id)?.name || "—";

  return (
    <>
      <div className="page-header">
        <h2 className="page-title">Фильмы</h2>
        <p className="page-subtitle">Каталог фильмов видеопроката</p>
      </div>

      <div className="page-body">
        {error && <div className="error-banner">{error}</div>}

        <div className="toolbar">
          <div className="search-wrap">
            <IconSearch />
            <input
              placeholder="Поиск по названию или режиссёру…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <button className="btn btn-primary" onClick={openAdd}>
            <IconPlus /> Добавить фильм
          </button>
        </div>

        <div className="card">
          {loading ? (
            <div className="loading">Загрузка…</div>
          ) : filtered.length === 0 ? (
            <div className="empty-state">
              <IconFilm />
              <p>
                {search ? "Ничего не найдено" : "Фильмов нет. Добавьте первый!"}
              </p>
            </div>
          ) : (
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>Код</th>
                    <th>Название</th>
                    <th>Режиссёр</th>
                    <th>Жанр</th>
                    <th>Год</th>
                    <th>Цена/день</th>
                    <th>Копий</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((m) => (
                    <tr key={m.id}>
                      <td className="td-mono">{m.movie_code}</td>
                      <td style={{ fontWeight: 500 }}>{m.title}</td>
                      <td className="td-muted">{m.director}</td>
                      <td>{catName(m.category_id)}</td>
                      <td className="td-muted">{m.release_year}</td>
                      <td>{m.price} ₽</td>
                      <td>
                        <span
                          className={`badge ${m.copies_count > 0 ? "badge-green" : "badge-gray"}`}
                        >
                          {m.copies_count}
                        </span>
                      </td>
                      <td>
                        <div className="flex-gap">
                          <button
                            className="btn btn-secondary btn-sm"
                            onClick={() => openCopies(m)}
                          >
                            <IconDisc /> Копии
                          </button>
                          <button
                            className="btn btn-secondary btn-sm"
                            onClick={() => openEdit(m)}
                          >
                            Изменить
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {showAddModal && (
        <Modal
          title={editMovie ? "Изменить фильм" : "Добавить фильм"}
          onClose={() => setShowAddModal(false)}
          size="lg"
        >
          {error && <div className="error-banner">{error}</div>}
          <form onSubmit={handleSave}>
            <div className="form-grid">
              <div className="form-group">
                <label>Название</label>
                <input
                  required
                  value={form.title}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, title: e.target.value }))
                  }
                />
              </div>
              <div className="form-group">
                <label>Режиссёр</label>
                <input
                  required
                  value={form.director}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, director: e.target.value }))
                  }
                />
              </div>
              <div className="form-group full">
                <label>Актёры</label>
                <input
                  required
                  value={form.actors}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, actors: e.target.value }))
                  }
                />
              </div>
              <div className="form-group">
                <label>Страна</label>
                <input
                  required
                  value={form.country}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, country: e.target.value }))
                  }
                />
              </div>
              <div className="form-group">
                <label>Жанр</label>
                <select
                  required
                  value={form.category_id}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, category_id: e.target.value }))
                  }
                >
                  <option value="">— выберите —</option>
                  {categories.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Год выпуска</label>
                <input
                  type="number"
                  required
                  value={form.release_year}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, release_year: e.target.value }))
                  }
                />
              </div>
              <div className="form-group">
                <label>Возрастной рейтинг</label>
                <select
                  value={form.age_rating}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, age_rating: e.target.value }))
                  }
                >
                  {[0, 6, 12, 16, 18].map((r) => (
                    <option key={r} value={r}>
                      {r}+
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Языки дублирования</label>
                <input
                  required
                  value={form.dubbing_languages}
                  onChange={(e) =>
                    setForm((f) => ({
                      ...f,
                      dubbing_languages: e.target.value,
                    }))
                  }
                />
              </div>
              <div className="form-group">
                <label>Цена аренды (₽/день)</label>
                <input
                  type="number"
                  min="0"
                  required
                  value={form.price}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, price: e.target.value }))
                  }
                />
              </div>
              <div className="form-group full">
                <label>Описание</label>
                <textarea
                  required
                  value={form.description}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, description: e.target.value }))
                  }
                />
              </div>
            </div>
            <div className="form-actions">
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => setShowAddModal(false)}
              >
                Отмена
              </button>
              <button
                type="submit"
                className="btn btn-primary"
                disabled={saving}
              >
                {saving ? "Сохранение…" : "Сохранить"}
              </button>
            </div>
          </form>
        </Modal>
      )}

      {copiesMovie && (
        <Modal
          title={`Копии — ${copiesMovie.title}`}
          onClose={() => setCopiesMovie(null)}
          size="lg"
        >
          <div style={{ marginBottom: 16 }}>
            <div
              className="flex-gap"
              style={{ marginBottom: 12, alignItems: "center" }}
            >
              <input
                type="number"
                min="1"
                max="20"
                value={copiesCount}
                onChange={(e) => setCopiesCount(+e.target.value)}
                style={{ width: 80 }}
              />
              <select
                value={copiesMediaType}
                onChange={(e) => setCopiesMediaType(e.target.value)}
              >
                <option value="DVD">DVD</option>
                <option value="CD">CD</option>
                <option value="VHS">VHS</option>
              </select>
              <button
                className="btn btn-primary"
                onClick={handleAddCopies}
                disabled={addingCopies}
              >
                <IconPlus /> Добавить копии
              </button>
            </div>
          </div>
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Инв. №</th>
                  <th>Тип носителя</th>
                  <th>Статус</th>
                </tr>
              </thead>
              <tbody>
                {copies.map((c) => (
                  <tr key={c.id}>
                    <td className="td-mono">{c.inventory_code}</td>
                    <td className="td-muted">{c.media_type}</td>
                    <td>
                      <span
                        className={`badge ${c.status === "available" ? "badge-green" : "badge-yellow"}`}
                      >
                        {c.status === "available" ? "Доступна" : "Выдана"}
                      </span>
                    </td>
                  </tr>
                ))}
                {copies.length === 0 && (
                  <tr>
                    <td
                      colSpan={3}
                      className="td-muted"
                      style={{ textAlign: "center", padding: 32 }}
                    >
                      Копий нет
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </Modal>
      )}
    </>
  );
}
